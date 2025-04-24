import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel, Field

from data_fetcher.src.library.models.library_model import (
    Contact,
    DaySchedule,
    Library,
    OpeningHours,
)
from shared.src.core.logging import get_library_logger
from shared.src.factories.llm_factory import LLMFactory
from shared.src.models.llm_message_models import SystemMessage, UserMessage
from shared.src.models.location_model import Location, Locations
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
                "User-Agent": "MunichLibraryFetcher/1.0 (https://github.com/lmu-dev/lmu_app_backend; admin@lmu-dev.org)"  # Replace with actual info
            }
        )
        self.geocoding_service = GeocodingService(user_agent="MunichLibraryCrawler/1.0 (contact@example.com)")

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

    def _generate_opening_hours(self, opening_hours_div: Tag) -> Optional[OpeningHours]:
        """Parse opening hours div into OpeningHours model."""
        if not opening_hours_div:
            return None

        # Get raw text, preserving line structure where possible
        raw_text = opening_hours_div.get_text(separator="\n").strip()
        # Basic cleanup
        raw_text = re.sub(r"^\s*Öffnungszeiten\s*", "", raw_text, flags=re.IGNORECASE).strip()
        if not raw_text:
            return None

        opening_hours = OpeningHours(semester=[], semester_break=[], notes=None, raw_text=raw_text)

        def parse_time_range(time_str: str) -> Optional[Dict[str, str]]:
            # Flexible pattern: 8:00, 08:00, 8-12, 8:00 - 12:00, etc.
            # Allows optional minutes, different separators
            time_pattern = r"(\d{1,2}(?::\d{2})?)\s*(?:-|–)\s*(\d{1,2}(?::\d{2})?)"
            match = re.search(time_pattern, time_str)
            if match:
                # Basic normalization (add :00 if missing) - might need more robust logic
                start = match.group(1)
                end = match.group(2)
                start = start if ":" in start else f"{start}:00"
                end = end if ":" in end else f"{end}:00"
                return {"start": start, "end": end}
            return None

        def parse_day_schedule(line: str) -> Optional[DaySchedule]:
            line = line.replace("–", "-").replace("Uhr", "").strip().strip(":")
            if not line:
                return None

            # Handle "geschlossen" separately
            if "geschlossen" in line.lower():
                # Try to find which days it applies to
                days_str_match = re.match(r"^(.*?)(?:\s*geschlossen)", line, re.IGNORECASE)
                days_str = (
                    days_str_match.group(1).strip() if days_str_match else line
                )  # Assume whole line if no explicit "geschlossen"
                time_ranges = [{"start": "geschlossen", "end": "geschlossen"}]
            else:
                # Find time ranges first
                time_ranges = []
                # Split by common separators like 'und', ',' while keeping times intact
                time_parts = re.split(r"\s+(?:und|,)\s+", line)
                extracted_times_str = ""
                for part in time_parts:
                    time_range = parse_time_range(part)
                    if time_range:
                        time_ranges.append(time_range)
                        extracted_times_str += part  # Keep track of text part containing times
                if not time_ranges:
                    return None  # No valid time found

                # Extract days part (text before the first time range found)
                days_str = line.split(extracted_times_str)[0].strip() if extracted_times_str else line
                days_str = days_str.strip(": ")

            if not days_str:
                return None  # Could not determine days

            day_names = [
                "Montag",
                "Dienstag",
                "Mittwoch",
                "Donnerstag",
                "Freitag",
                "Samstag",
                "Sonntag",
            ]
            day_map = {name.lower(): name for name in day_names}
            days_list = []

            # Check for ranges (Mo-Fr, etc.)
            range_match = re.match(r"(\w+)\s*-\s*(\w+)", days_str, re.IGNORECASE)
            if range_match:
                start_day_str = range_match.group(1).lower()
                end_day_str = range_match.group(2).lower()
                if start_day_str in day_map and end_day_str in day_map:
                    start_idx = day_names.index(day_map[start_day_str])
                    end_idx = day_names.index(day_map[end_day_str])
                    if start_idx <= end_idx:
                        days_list = day_names[start_idx : end_idx + 1]
            # If no range match or invalid range, look for individual days
            if not days_list:
                individual_days = re.findall(
                    r"\b(Mo|Di|Mi|Do|Fr|Sa|So|Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)\b",
                    days_str,
                    re.IGNORECASE,
                )
                day_abbr_map = {
                    "mo": "Montag",
                    "di": "Dienstag",
                    "mi": "Mittwoch",
                    "do": "Donnerstag",
                    "fr": "Freitag",
                    "sa": "Samstag",
                    "so": "Sonntag",
                }
                for day in individual_days:
                    day_lower = day.lower()
                    full_day_name = day_map.get(day_lower) or day_abbr_map.get(day_lower)
                    if full_day_name and full_day_name not in days_list:
                        days_list.append(full_day_name)

            if not days_list:
                return None  # Failed to parse days

            return DaySchedule(days=sorted(days_list, key=day_names.index), times=time_ranges)

        # --- Parsing Logic ---
        current_section_list = opening_hours.semester  # Default to semester
        notes_accumulator = []
        in_notes_section = False

        # Use BS4 to find relevant sections if possible
        semester_header = opening_hours_div.find(string=re.compile(r"^\s*Semester|Vorlesungszeit", re.IGNORECASE))
        break_header = opening_hours_div.find(string=re.compile(r"Vorlesungsfreie Zeit|Semesterferien", re.IGNORECASE))

        # Iterate through elements within the div
        for element in opening_hours_div.children:
            text = ""
            if isinstance(element, Tag):
                text = element.get_text(strip=True)
            elif isinstance(element, str):
                text = element.strip()

            if not text:
                continue

            # Detect section changes based on headers (case-insensitive)
            text_lower = text.lower()
            if "semester" in text_lower or "vorlesungszeit" in text_lower:
                current_section_list = opening_hours.semester
                in_notes_section = False
                continue  # Skip the header line itself
            elif "vorlesungsfreie zeit" in text_lower or "semesterferien" in text_lower:
                current_section_list = opening_hours.semester_break
                in_notes_section = False
                continue  # Skip the header line itself

            # Attempt to parse as a day schedule
            schedule = parse_day_schedule(text)
            if schedule:
                # Ensure the target list exists
                if current_section_list is None:
                    if current_section_list is opening_hours.semester:
                        opening_hours.semester = []
                        current_section_list = opening_hours.semester
                    else:
                        opening_hours.semester_break = []
                        current_section_list = opening_hours.semester_break
                current_section_list.append(schedule)
                in_notes_section = False  # Parsed schedule, likely not notes anymore
            else:
                # If not parsable as schedule, treat as potential note
                # Avoid adding simple headers again
                if not (
                    "semester" in text_lower
                    or "vorlesungszeit" in text_lower
                    or "vorlesungsfreie zeit" in text_lower
                    or "semesterferien" in text_lower
                ):
                    notes_accumulator.append(text)
                    in_notes_section = True

        if notes_accumulator:
            opening_hours.notes = "\n".join(notes_accumulator).strip()

        # Cleanup empty lists
        if not opening_hours.semester:
            opening_hours.semester = None
        if not opening_hours.semester_break:
            opening_hours.semester_break = None

        # If only notes were found, clear schedule lists
        if opening_hours.notes and not opening_hours.semester and not opening_hours.semester_break:
            # Check if notes *only* say something like "geschlossen"
            if opening_hours.notes.lower() == "geschlossen":
                opening_hours.semester = [
                    DaySchedule(
                        days=[
                            "Montag",
                            "Dienstag",
                            "Mittwoch",
                            "Donnerstag",
                            "Freitag",
                            "Samstag",
                            "Sonntag",
                        ],
                        times=[{"start": "geschlossen", "end": "geschlossen"}],
                    )
                ]
                opening_hours.notes = None  # Clear notes as it's represented in schedule
            else:
                # Keep notes, but ensure schedules are None
                opening_hours.semester = None
                opening_hours.semester_break = None

        # Return None if the entire structure is empty
        if not opening_hours.semester and not opening_hours.semester_break and not opening_hours.notes:
            return None

        return opening_hours

    def _clean_contact_info(self, contact_data: Dict[str, Any]) -> Optional[Contact]:
        """Clean and structure contact information into ContactInfo model."""
        cleaned = Contact()

        print(contact_data)

        # Address parsing
        if contact_data.get("address"):
            cleaned.location = self._generate_locations(contact_data["address"])

        # Email extraction and validation
        emails = []
        if contact_data.get("email"):
            potential_emails = (
                contact_data["email"] if isinstance(contact_data["email"], list) else [contact_data["email"]]
            )
            for email in potential_emails:
                valid_emails = self._extract_emails(email)  # Use extractor for validation
                emails.extend(valid_emails)
        # Fallback: Extract from address if no email found yet
        if not emails and cleaned.location and cleaned.location[0].address:
            emails.extend(self._extract_emails(cleaned.location[0].address))
        cleaned.email = sorted(list(set(emails))) or None

        # Phone extraction and structuring
        phones = []
        if contact_data.get("phone"):
            phones.extend(self._generate_phone_numbers(contact_data["phone"]))
        # Fallback: Extract from address
        if not phones and cleaned.location and cleaned.location[0].address:
            phones.extend(self._generate_phone_numbers(cleaned.location[0].address))
        # Structure phone numbers
        unique_phones = sorted(list(set(p for p in phones if p)))
        if unique_phones:
            # Ensure phone structure matches the model definition
            cleaned.phone = {
                "main": unique_phones[0],
                "additional": unique_phones[1:] if len(unique_phones) > 1 else None,
            }

        # Website validation
        website = contact_data.get("website")
        if website and isinstance(website, str):
            parsed_url = urlparse(website)
            if parsed_url.scheme in ["http", "https"] and parsed_url.netloc:
                cleaned.website = website
            else:
                logger.warning(f"Invalid or relative website URL found and skipped: {website}")

        # Return None if no contact info was actually found
        # FIX: Access model_fields via class, not instance
        if not any(
            getattr(cleaned, field)
            for field in Contact.model_fields
            if field != "location"
            or (cleaned.location and any(getattr(cleaned.location[0], afield) for afield in Location.model_fields))
        ):
            return None

        return cleaned

    def _parse_library_details(self, url: str, name: str, location_number: List[str]) -> Library:
        """Parse detailed information from a library's individual page."""
        soup = self._get_page(url)
        if not soup:
            logger.warning(f"Failed to fetch or parse page for {name}: {url}")
            # Return minimal Library object on failure
            return Library(name=name, location_number=location_number, url=url)

        # Find the main content area (adjust selectors if needed)
        content_div = soup.find("div", {"class": "content content-einrichtung"}) or soup.find("div", id="content")
        if not content_div:
            logger.warning(f"Could not find main content div for {name}: {url}")
            return Library(name=name, location_number=location_number, url=url)

        # --- Initialize data dictionary ---
        details = {
            "contact": {},
            "opening_hours": None,
            "transportation": None,
            "services": [],
            "subject_areas": [],
            "notes": [],  # Collect various notes/texts here
        }

        # --- Extract Contact Info ---
        contact_div = content_div.find("div", {"class": "bd-kontakt"})
        if contact_div:
            # Address
            address_elem = contact_div.find("address", {"class": "g-address"})
            if address_elem:
                details["contact"]["address"] = address_elem.get_text(separator="\n").strip()
            # Phone
            phone_elem = contact_div.find("p", {"class": "telefon"})
            if phone_elem:
                phone_text = phone_elem.get_text(strip=True)
                details["contact"]["phone"] = re.sub(r"^Telefon:\s*", "", phone_text, flags=re.IGNORECASE).strip()
            # Fax
            fax_elem = contact_div.find("p", {"class": "fax"})
            if fax_elem:
                fax_text = fax_elem.get_text(strip=True)
                details["contact"]["fax"] = re.sub(r"^Fax:\s*", "", fax_text, flags=re.IGNORECASE).strip()
            # Website
            website_div = contact_div.find("div", class_="webadresse")
            if website_div:
                website_link = website_div.find("a")
                if website_link and website_link.has_attr("href"):
                    details["contact"]["website"] = urljoin(self.BASE_URL, website_link["href"])
            # Email (try mailto link first, then search text)
            email_link = contact_div.find("a", href=lambda href: href and href.startswith("mailto:"))
            if email_link:
                details["contact"]["email"] = email_link["href"].replace("mailto:", "")
            else:
                emails_in_contact = self._extract_emails(contact_div.get_text())
                details["contact"]["email"] = emails_in_contact

        # --- Extract Opening Hours ---
        opening_hours_div = content_div.find("div", {"class": "oeffnungszeiten"})
        if opening_hours_div:
            details["opening_hours"] = self._generate_opening_hours(opening_hours_div)
        else:
            # Sometimes hours are under a simple H3/H2
            hours_header = content_div.find(["h2", "h3"], string=re.compile(r"Öffnungszeiten", re.IGNORECASE))
            if hours_header:
                # Find the div/p/ul elements following the header
                hours_content_elements = self._extract_section_content(hours_header)
                hours_text = "\n".join(
                    elem.get_text(strip=True) if isinstance(elem, Tag) else elem for elem in hours_content_elements
                )
                # Simulate a div structure for the parser
                pseudo_div = BeautifulSoup(f"<div>{hours_text}</div>", "html.parser").div
                if pseudo_div:
                    details["opening_hours"] = self._generate_opening_hours(pseudo_div)

        # --- Extract Transportation ---
        transport_header = content_div.find(
            ["h2", "h3"], string=re.compile(r"Verkehrsanbindung|Anfahrt", re.IGNORECASE)
        )
        if transport_header:
            transport_content = self._extract_section_content(transport_header)
            details["transportation"] = self._parse_transportation_section(transport_content)

        # --- Extract Services (Ausstattung) & Subject Areas (Sammelgebiete) ---
        service_header = content_div.find(["h2", "h3"], string=re.compile(r"Service|Ausstattung", re.IGNORECASE))
        if service_header:
            service_content = self._extract_section_content(service_header)
            details["services"].extend(self._extract_list_items(service_content))

        subject_header = content_div.find(["h2", "h3"], string=re.compile(r"Sammelgebiete|Fachgebiete", re.IGNORECASE))
        if subject_header:
            subject_content = self._extract_section_content(subject_header)
            details["subject_areas"].extend(self._extract_list_items(subject_content))

        # --- Consolidate and Clean ---
        # Remove duplicates and empty strings
        details["services"] = sorted(list(set(s for s in details["services"] if s))) or None
        details["subject_areas"] = sorted(list(set(s for s in details["subject_areas"] if s))) or None
        final_notes = "\n".join(n for n in details["notes"] if n).strip() or None

        final_contact = self._clean_contact_info(details["contact"])

        # --- Create Library Model ---
        try:
            library = Library(
                name=name,
                location_number=location_number,
                url=url,
                contact=final_contact,
                opening_hours=details["opening_hours"],
                services=details["services"],
                subject_areas=details["subject_areas"],
                transportation=details["transportation"],
                notes=final_notes,  # Combine collected notes here if needed
            )
            return library
        except Exception as e:
            logger.error(f"Failed to instantiate Library model for {name} ({url}): {e}")
            # Return minimal object on model error
            return Library(name=name, location_number=location_number, url=url)

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
                        # Decide if you want to proceed without location numbers
                        # continue

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
                # Optional delay to be polite
                time.sleep(0.5)  # Adjust as needed
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

    # locations = crawler._generate_locations("Ludwigstraße 25, 80539 München")
    # print(locations)
    phones = crawler._generate_phone_numbers("Telefon: 089 289-27686\n089 289-27546 Dr. Alexander Schütze")
    print(phones)
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
