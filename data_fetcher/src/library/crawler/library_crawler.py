import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field

from data_fetcher.src.core.html_utils import html_to_markdown
from data_fetcher.src.library.models.library_model import (
    Contact,
    Equipment,
    Library,
    OpeningHours,
)
from shared.src.core.logging import get_library_logger
from shared.src.factories.llm_factory import LLMFactory
from shared.src.models.link_model import Link
from shared.src.models.llm_message_models import SystemMessage, UserMessage
from shared.src.models.location_model import Locations
from shared.src.models.phone_model import Phones
from shared.src.services.geocoding_service import GeocodingService

logger = get_library_logger(__name__)


class LibraryCrawler:
    """
    Crawls the LMU UB website for library information, parses details,
    and returns structured library data.
    """

    BASE_URL = "https://www.ub.uni-muenchen.de"
    LIBRARIES_BASE_PATH = "/bibliotheken/bibs-a-bis-z"
    LIBRARIES_URL = f"{BASE_URL}{LIBRARIES_BASE_PATH}/index.html"

    def __init__(self):
        """Initializes the crawler session and geolocator."""
        self.session = requests.Session()
        self.llm = LLMFactory(
            provider="openai",
        )
        # Set a more descriptive user agent
        self.session.headers.update(
            {
                "User-Agent": "MunichLibraryFetcher/1.0 (https://github.com/lmu-devs/lmu_app_backend; admin@lmu-devs.com)"  # Replace with actual info
            }
        )
        self.geocoding_service = GeocodingService(user_agent="MunichLibraryCrawler/1.0 (admin@lmu-devs.com)")

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return its BeautifulSoup object."""
        try:
            response = self.session.get(url, timeout=15)  # Add timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            # Check content type to avoid parsing non-HTML content
            if "html" not in response.headers.get("Content-Type", "").lower():
                logger.warning(f"Non-HTML content type received from {url}")
                return None
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            # Catch potential BS4 parsing errors too
            logger.error(f"Error processing page {url}: {str(e)}")
            return None

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not text:
            return []
        # Improved regex to avoid matching things like "javascript:"
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        return re.findall(email_pattern, text)

    def _generate_phone_numbers(self, text: str) -> Phones:
        """Extract and normalize phone numbers."""
        if not text:
            return []

        class Response(BaseModel):
            phones: Phones = Field(
                description="The phone numbers of the library, in edge cases there might be multiple phone numbers"
            )

        response: Response = self.llm.create_completion(
            model="gpt-4.1-mini",
            messages=[
                SystemMessage(
                    content="You are a phone number parser. You are given a string of text that contains phone numbers. You need to parse the phone numbers into a structured format."
                ),
                UserMessage(content=text),
            ],
            response_model=Response,
        )

        return response.phones

    def _generate_locations(self, address_text: str) -> Locations:
        """Parse address into Locations model."""
        if not address_text:
            return []

        class Address(BaseModel):
            address: str = Field(
                description="The address of the library. Format the address like this: 'Street Nr, Postal Code City, City'"
            )
            room: str | None = Field(description="The room/location of the library, if it is known")

        class Response(BaseModel):
            addresses: List[Address] = Field(
                description="The address of the library, in edge cases there might be multiple addresses"
            )

        response: Response = self.llm.create_completion(
            model="gpt-4.1-mini",
            messages=[
                SystemMessage(
                    content="You are a location parser. You are given a string of text that contains an address. You need to parse the address into a structured format."
                ),
                UserMessage(content=address_text),
            ],
            response_model=Response,
        )

        print(response)

        locations = []
        for address in response.addresses:
            location = self.geocoding_service.get_location(address.address)
            # TODO: Add room to location?
            if location:
                locations.append(location)
        return locations

    def _generate_opening_hours(self, opening_hours_text: str) -> OpeningHours | None:
        """Parse opening hours div into OpeningHours model."""
        if not opening_hours_text:
            return None

        response: OpeningHours = self.llm.create_completion(
            model="gpt-4.1-mini",
            messages=[
                SystemMessage(
                    content="You are a opening hours parser. You are given a string of text that contains opening hours. You need to parse the opening hours into a structured format."
                ),
                UserMessage(content=opening_hours_text),
            ],
            response_model=OpeningHours,
        )

        return response

    def _extract_section_content(self, section_tag: Tag, stop_tags=["h1", "h2", "h3", "h4"]) -> List[Union[Tag, str]]:
        """Extract sibling elements following a section tag until the next heading."""
        content = []
        current_element = section_tag.next_sibling
        while current_element:
            if isinstance(current_element, Tag):
                # Stop if we hit the next heading of the same or higher level
                if current_element.name in stop_tags:
                    break
                # Keep relevant tags like paragraphs, lists, divs
                if current_element.name in ["p", "ul", "ol", "div", "dl", "table"]:
                    content.append(current_element)
            elif isinstance(current_element, str) and current_element.strip():
                # Keep non-empty text nodes
                content.append(current_element.strip())
            current_element = current_element.next_sibling
        return content

    def _extract_list_items(self, content_elements: List[Union[Tag, str]]) -> List[str]:
        """Extract meaningful text from list items or paragraphs within content elements."""
        items = []
        for elem in content_elements:
            if isinstance(elem, Tag):
                # Extract text from lists (ul, ol)
                if elem.name in ["ul", "ol"]:
                    for li in elem.find_all("li", recursive=False):  # Only direct children
                        text = li.get_text(strip=True)
                        if text:
                            items.append(text)
                # Extract text from paragraphs if not empty
                elif elem.name == "p":
                    text = elem.get_text(strip=True)
                    if text:
                        items.append(text)
                # Could add handling for other tags like 'dl', 'table' if needed
            elif isinstance(elem, str) and elem.strip():
                # Append non-empty strings directly
                items.append(elem)
        return items  # Returns list of non-empty strings

    def _parse_transportation_section(self, content_elements: List[Union[Tag, str]]) -> Optional[str]:
        """Extract transportation info, usually found in <p> tags."""
        transport_text = []
        for elem in content_elements:
            if isinstance(elem, Tag) and elem.name == "p":
                text = elem.get_text(strip=True)
                # Add checks to filter out irrelevant paragraphs if necessary
                if text and not any(kw in text.lower() for kw in ["lageplan", "lmu raumfinder"]):
                    transport_text.append(text)
            elif isinstance(elem, str) and elem.strip():
                # Include relevant text nodes too
                if not any(kw in elem.lower() for kw in ["lageplan", "lmu raumfinder"]):
                    transport_text.append(elem)

        return "\n".join(transport_text).strip() or None

    def _parse_access_regulation_section(
        self, content_elements: List[Union[Tag, str]]
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Extract access regulation info and reservation URL.

        Args:
            content_elements: List of HTML elements containing access regulation content

        Returns:
            Tuple of (access_regulation_text, reservation_url)
        """
        access_text = []
        reservation_url = None

        for elem in content_elements:
            if isinstance(elem, Tag):
                if elem.name == "p":
                    # Check for reservation link
                    link = elem.find("a", href=True)
                    if link and "reservierung" in link.get_text().lower():
                        reservation_url = link["href"]

                    # Get text content
                    text = elem.get_text(strip=True)
                    if text and not any(kw in text.lower() for kw in ["leseplatzreservierung", "reservierung"]):
                        access_text.append(text)
            elif isinstance(elem, str) and elem.strip():
                access_text.append(elem)

        return ("\n".join(access_text).strip() or None, reservation_url)

    def _generate_content_hash(self, soup: BeautifulSoup) -> str:
        """
        Generate a hash of the entire webpage content.

        Args:
            soup: BeautifulSoup object of the webpage

        Returns:
            str: A hex digest of the content hash
        """
        if not soup:
            return hashlib.sha256("empty".encode()).hexdigest()

        # Get all text content from the page, normalized
        content = soup.get_text(separator=" ", strip=True)
        # Normalize whitespace and convert to lowercase for stable hashing
        content = " ".join(content.lower().split())

        return hashlib.sha256(content.encode()).hexdigest()

    def _get_contact(self, content_div: Tag) -> Optional[Contact]:
        """Clean and structure contact information into ContactInfo model."""
        contact = Contact()

        # Extract contact info from content div
        contact_div = content_div.find("div", {"class": "bd-kontakt"})
        if contact_div:
            # Address
            address_elem = contact_div.find("address", {"class": "g-address"})
            if address_elem:
                address = address_elem.get_text(separator="\n").strip()
                contact.location = self._generate_locations(address)

            # Phone
            phone_elem = contact_div.find("p", {"class": "telefon"})
            if phone_elem:
                phone_text = phone_elem.get_text(strip=True)
                phone = re.sub(r"^Telefon:\s*", "", phone_text, flags=re.IGNORECASE).strip()
                contact.phone = self._generate_phone_numbers(phone)

            # Website
            website_div = contact_div.find("div", class_="webadresse")
            if website_div:
                website_link = website_div.find("a")
                if website_link and website_link.has_attr("href"):
                    website = urljoin(self.BASE_URL, website_link["href"])
                    # Website validation
                    parsed_url = urlparse(website)
                    if parsed_url.scheme in ["http", "https"] and parsed_url.netloc:
                        contact.website = website
                    else:
                        logger.warning(f"Invalid or relative website URL found and skipped: {website}")

            # Email (try mailto link first, then search text)
            email_link = contact_div.find("a", href=lambda href: href and href.startswith("mailto:"))
            if email_link:
                emails = [email_link["href"].replace("mailto:", "")]
            else:
                emails = self._extract_emails(contact_div.get_text())

            # Clean and validate emails
            emails = []
            if emails:
                for email in emails:
                    valid_emails = self._extract_emails(email)
                    emails.extend(valid_emails)
            # Fallback: Extract from address if no email found yet
            if not emails and contact.location and contact.location[0].address:
                emails.extend(self._extract_emails(contact.location[0].address))
            contact.email = sorted(list(set(emails))) or None

            # Fallback phone extraction from address if not found earlier
            if not contact.phone and contact.location and contact.location[0].address:
                phones = self._generate_phone_numbers(contact.location[0].address)
                if phones:
                    contact.phone = {
                        "main": phones[0],
                        "additional": phones[1:] if len(phones) > 1 else None,
                    }

        return contact

    def _parse_library_details(self, url: str, name: str, location_number: List[str]) -> Library:
        """Parse detailed information from a library's individual page."""
        # Extract library ID from URL
        library_id = url.split("/")[-2] if url.split("/")[-1] == "index.html" else None

        soup = self._get_page(url)
        if not soup:
            logger.warning(f"Failed to fetch or parse page for {name}: {url}")
            # Return minimal Library object on failure
            return Library(
                id=library_id,
                name=name,
                location_number=location_number,
                url=url,
                hash="error_fetching_page",
            )

        # Generate content hash first
        content_hash = self._generate_content_hash(soup)

        # Find the main content area (adjust selectors if needed)
        content_div = soup.find("div", {"class": "content content-einrichtung"}) or soup.find("div", id="content")
        if not content_div:
            logger.warning(f"Could not find main content div for {name}: {url}")
            return Library(
                id=library_id,  # Add ID here
                name=name,
                location_number=location_number,
                url=url,
                hash=content_hash,
            )

        # --- Initialize data ---
        opening_hours: OpeningHours | None = None
        contact: Contact = self._get_contact(content_div)
        transportation: str | None = None
        access_regulation: str | None = None
        services: List[str] = []
        subject_areas: List[str] = []
        equipment: List[Equipment] = []

        # --- Extract Opening Hours ---
        opening_hours_div = content_div.find("div", {"class": "oeffnungszeiten"})
        if opening_hours_div:
            # Convert opening hours to clean markdown text
            text_content = html_to_markdown(opening_hours_div)
            opening_hours = self._generate_opening_hours(text_content)

        # --- Extract Transportation ---
        transport_header = content_div.find(
            ["h2", "h3"], string=re.compile(r"Verkehrsanbindung|Anfahrt", re.IGNORECASE)
        )
        if transport_header:
            transport_content = self._extract_section_content(transport_header)
            transportation = self._parse_transportation_section(transport_content)

        # --- Extract Access Regulation ---
        access_header = content_div.find(["h2", "h3"], string=re.compile(r"Zugangsregelung", re.IGNORECASE))
        if access_header:
            access_content = self._extract_section_content(access_header)
            access_regulation, reservation_url = self._parse_access_regulation_section(access_content)

        # --- Extract Services (Ausstattung) ---
        service_header = content_div.find(["h2", "h3"], string=re.compile(r"Service", re.IGNORECASE))
        if service_header:
            service_content = self._extract_section_content(service_header)
            services.extend(self._extract_list_items(service_content))

        # --- Extract Equipment ---
        equipment_header = content_div.find(["h2", "h3"], string=re.compile(r"Ausstattung", re.IGNORECASE))
        equipment = []
        if equipment_header:
            equipment_content = self._extract_section_content(equipment_header)
            equipment_text = html_to_markdown("\n".join(str(elem) for elem in equipment_content))
            # Split by commas and clean up
            equipment_items = [item.strip() for item in equipment_text.split(",")]
            for item in equipment_items:
                if item:
                    # Check if item has a link
                    url = None
                    link_match = re.search(r"\[(.*?)\]\((.*?)\)", item)
                    if link_match:
                        name = link_match.group(1)
                        url = link_match.group(2)
                    else:
                        name = item
                    equipment.append(Equipment(name=name, url=url))

        # --- Extract Subject Areas (Sammelgebiete) ---
        subject_header = content_div.find(["h2", "h3"], string=re.compile(r"Sammelgebiete|Fachgebiete", re.IGNORECASE))
        if subject_header:
            subject_content = self._extract_section_content(subject_header)
            subject_areas.extend(self._extract_list_items(subject_content))

        # --- Consolidate and Clean ---
        # Remove duplicates and empty strings
        services = sorted(list(set(s for s in services if s))) or None
        subject_areas = sorted(list(set(s for s in subject_areas if s))) or None

        # --- Create Library Model ---
        try:
            library = Library(
                id=library_id,
                name=name,
                hash=content_hash,
                location_number=location_number,
                url=url,
                contact=contact,
                access_regulation=access_regulation,
                opening_hours=opening_hours,
                services=services,
                equipment=equipment,
                subject_areas=subject_areas,
                transportation=transportation,
            )
            print(library.model_dump_json(indent=2))
            return library
        except Exception as e:
            logger.error(f"Failed to instantiate Library model for {name} ({url}): {e}")
            # Return minimal object on model error
            return Library(
                id=library_id,
                name=name,
                location_number=location_number,
                url=url,
                hash="error_creating_model",
            )

    def _parse_libraries_list(self) -> List[Dict[str, Any]]:
        """Parse the main libraries list page (A-Z) to get names, URLs, and location numbers."""
        base_libraries_info = []
        soup = self._get_page(self.LIBRARIES_URL)
        if not soup:
            logger.error("Could not fetch the main library list page. Aborting.")
            return base_libraries_info

        tables = soup.find_all("table", {"class": "contenttable"})  # Target specific tables if possible
        if not tables:
            logger.warning("No tables with class 'contenttable' found on the library list page.")
            # Fallback? Find all tables?
            tables = soup.find_all("table")

        processed_urls = set()  # Avoid processing the same library page multiple times

        for table in tables:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:  # Need at least name and number columns
                    name_cell, number_cell = cells[0], cells[1]
                    link = name_cell.find("a")

                    if link and link.has_attr("href"):
                        name = link.get_text(strip=True)
                        href = link["href"]

                        # Skip anchors or javascript links
                        if href.startswith("#") or href.startswith("javascript:"):
                            continue

                        # Construct absolute URL
                        # Handles cases like /path/page.html and relative/page.html
                        url = urljoin(self.LIBRARIES_URL, href)  # Use LIBRARIES_URL as base

                        # Skip if already processed
                        if url in processed_urls:
                            continue
                        processed_urls.add(url)

                        # Extract location numbers cleanly
                        location_numbers = [
                            num.strip()
                            for num in number_cell.get_text(separator=",").split(",")
                            if num.strip().isdigit()
                        ]

                        if not name:
                            logger.warning(f"Skipping row with empty name, URL: {url}, Numbers: {location_numbers}")
                            continue
                        if not location_numbers:
                            logger.warning(f"Skipping library '{name}' with no valid location numbers: {url}")

                        base_libraries_info.append(
                            {
                                "name": name,
                                "url": url,
                                "location_numbers": location_numbers,
                            }
                        )
        logger.info(f"Found {len(base_libraries_info)} potential libraries from the list page.")
        return base_libraries_info

    def get_libraries(self) -> List[Library]:
        """
        Fetches the list of libraries, then crawls each library's detail page.

        Returns:
            List[Library]: A list of populated Library models.
        """
        logger.info("Starting library crawl process...")
        libraries_data: List[Library] = []

        # 1. Get the basic list of libraries (Name, URL, Location Numbers)
        base_library_list = self._parse_libraries_list()

        if not base_library_list:
            logger.error("No libraries found from the A-Z list page. Cannot proceed.")
            return libraries_data

        # 2. Crawl details for each library
        total = len(base_library_list)
        for i, lib_info in enumerate(base_library_list):
            logger.info(f"[{i + 1}/{total}] Processing: {lib_info['name']} ({lib_info['url']})")
            try:
                library_details = self._parse_library_details(
                    url=lib_info["url"],
                    name=lib_info["name"],
                    location_number=lib_info["location_numbers"],  # Pass list of numbers
                )
                libraries_data.append(library_details)
            except Exception as e:
                # Log error for this specific library but continue with others
                logger.error(
                    f"Unexpected error parsing details for {lib_info['name']} ({lib_info['url']}): {e}",
                    exc_info=True,
                )

        logger.info(f"Finished processing details for {len(libraries_data)} libraries.")
        return libraries_data


# --- Main execution block ---
def save_data_to_file(data: Dict, filename: str = "libraries.json"):
    """Save the final crawled data structure to a JSON file."""
    path = Path(filename)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            # Use Pydantic's json handling via model_dump for consistency
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data saved to {filename}")
    except TypeError as e:
        logger.error(f"Serialization error saving data to {filename}: {e}. Data might contain non-serializable types.")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")


if __name__ == "__main__":
    logger.info("Munich Library Crawler script started.")
    crawler = LibraryCrawler()
    crawler.get_libraries()

    # locations = crawler._generate_locations("Ludwigstraße 25, 80539 München")
    # print(locations)
    # phones = crawler._generate_phone_numbers("Telefon: 089 289-27686\n089 289-27546 Dr. Alexander Schütze")
    # print(phones)
#     opening_hours = crawler._generate_opening_hours(
#         """## Öffnungszeiten

# Semester
# Montag - Freitag 10:00 - 16:00 Uhr

# Vorlesungsfreie Zeit
# Nach Vereinbarung per E-Mail: [aegyptologie@aegyp.fak12.uni-muenchen.de](mailto:aegyptologie@aegyp.fak12.uni-muenchen.de "E-Mail senden an: aegyptologie@aegyp.fak12.uni-muenchen.de")"""
#     )
#     print(opening_hours)

# libraries: List[Library] = crawler.get_libraries()

# if libraries:
#     logger.info(f"Successfully crawled {len(libraries)} library entries.")
#     # Prepare final data structure for saving
#     output_data = {
#         "last_updated": datetime.now(UTC).isoformat(),
#         # Use model_dump for Pydantic models before saving
#         "libraries": [
#             lib.model_dump(mode="json", exclude_none=True) for lib in libraries
#         ],
#     }
#     save_data_to_file(
#         output_data, "libraries.json"
#     )  # Save in the current directory or specify a path
#     logger.info("Output saved to libraries.json")
# else:
#     logger.error("Crawling returned no library data. File not saved.")

# logger.info("Munich Library Crawler script finished.")
