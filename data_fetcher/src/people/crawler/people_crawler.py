import logging
import tqdm
import requests
import re
import time
from urllib.parse import urlencode
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import SSLError, ConnectionError, Timeout, RequestException
from shared.src.enums import AcademicTitle, LSFRole
from shared.src.core.logging import get_main_fetcher_logger

logger = get_main_fetcher_logger(__name__)


class LSFPersonCrawler:
    BASE = "https://lsf.verwaltung.uni-muenchen.de/qisserver/rds"
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    RESULTS_PER_PAGE = 50
    REQUEST_DELAY = 0  # Delay between requests to avoid overwhelming server (increase if you get rate limited)
    MAX_RETRIES = 3
    TIMEOUT = 30

    def __init__(self):
        self.session = self._create_session()
        self.functions = self._crawl_functions()
        logger.info(f"Found {len(self.functions)} roles to try.")
    
    def _create_session(self):
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _make_request(self, url: str, max_attempts: int = None) -> requests.Response:
        """Make a robust HTTP request with retry logic and error handling."""
        if max_attempts is None:
            max_attempts = self.MAX_RETRIES
            
        for attempt in range(max_attempts):
            try:
                time.sleep(self.REQUEST_DELAY)  # Add delay between requests
                response = self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
                response.raise_for_status()
                return response
                
            except SSLError as e:
                logger.warning(f"SSL error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except (ConnectionError, Timeout) as e:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except RequestException as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise RuntimeError(f"Failed to make request after {max_attempts} attempts")

    def _crawl_functions(self) -> dict[int, str]:
        # Pull the Funktion dropdown from the personSearch form
        params = {
            "state":           "change",
            "type":            "5",
            "moduleParameter": "personSearch",
            "nextdir":         "change",
            "next":            "search.vm",
            "subdir":          "person",
            "_form":           "display",
            "clean":           "y",
            "category":        "person.search",
        }
        r = self._make_request(f"{self.BASE}?{urlencode(params)}")
        tree = html.fromstring(r.content)

        sel = tree.xpath('//select[@id="r_funktion.pfid"]')
        if not sel:
            raise RuntimeError("Couldn't find the function dropdown!")
        sel = sel[0]

        funcs = {}
        for opt in sel.xpath(".//option"):
            val = opt.get("value").strip()
            txt = opt.text_content().strip()
            if val:
                funcs[int(val)] = txt
                logger.debug(f"Role {val}: {txt}")
        return funcs

    def crawl_first_function(self) -> list[dict]:
        """Crawl only the first available function."""
        if not self.functions:
            logger.error("No functions available!")
            return []

        # Start with role ID 1
        pfid = 1
        role_name = self.functions.get(pfid, "Unknown Role")
        logger.info(f"→ Searching role {pfid} ('{role_name}')…")
        people = self._crawl_role(pfid)

        if people:
            logger.info(f"   ✓ Found {len(people)} persons in '{role_name}'")
        else:
            logger.info(f"   – No entries for '{role_name}'")
        
        return people

    def crawl_all_functions(self) -> list[dict]:
        """Crawl all available functions."""
        if not self.functions:
            logger.error("No functions available!")
            return []

        all_people = []
        for pfid, role_name in self.functions.items():
            logger.info(f"→ Searching role {pfid} ('{role_name}')…")
            people = self._crawl_role(pfid)

            if people:
                # Add role information to each person
                for person in people:
                    person["role"] = {
                        "id": pfid,
                        "name": role_name
                    }
                all_people.extend(people)
                logger.info(f"   ✓ Found {len(people)} persons in '{role_name}'")
            else:
                logger.info(f"   – No entries for '{role_name}'")
        
        return all_people

    def crawl_single_role(self, pfid: int) -> list[dict]:
        """Crawl a single role by its ID."""
        if pfid not in self.functions:
            logger.error(f"Role ID {pfid} not found in available functions")
            return []
        
        role_name = self.functions[pfid]
        logger.info(f"→ Searching role {pfid} ('{role_name}')…")
        people = self._crawl_role(pfid)
        
        if people:
            # Add role information to each person
            for person in people:
                person["role"] = {
                    "id": pfid,
                    "name": role_name
                }
            logger.info(f"   ✓ Found {len(people)} persons in '{role_name}'")
        else:
            logger.info(f"   – No entries for '{role_name}'")
        
        return people

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing extra whitespace and newlines."""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove common prefixes
        text = re.sub(r'^(Name:|Funktion:|Dienstadresse:|E-Mail:|Dienstzimmer:)', '', text)
        return text.strip()

    def _extract_department_info(self, doc: html.HtmlElement) -> dict:
        """Extract department and position information from the page."""
        dept_info = {
            "faculty": None,
            "department": None,
            "positions": []
        }
        
        # Find the structure tree entries
        structure_entries = doc.xpath('//div[@style="padding-left: 20px;"]//a | //div[@style="padding-left: 30px;"]//a')
        for entry in structure_entries:
            text = self._clean_text(entry.text_content())
            if "Fakultät" in text:
                dept_info["faculty"] = text
            elif any(f"W{i}" in text for i in range(1, 4)):
                dept_info["positions"].append({
                    "title": text,
                    "academic_title": AcademicTitle.from_string(text).name,
                    "url": entry.get("href")
                })
            else:
                # If it's not a faculty or position, it's likely a department
                dept_info["department"] = text
        
        return dept_info

    def _extract_person_details(self, doc: html.HtmlElement) -> dict:
        """Extract detailed information about a person from their detail page."""
        details = {
            "basic_info": {},
            "faculty": None,
            "roles": [],
            "courses": []
        }
        
        # Define a mapping from the th#id → your JSON key
        id_map = {
            "basic_1": "last_name",
            "basic_2": "gender",
            "basic_3": "first_name",
            "basic_4": "office_hours",       # Sprechzeit
            "basic_5": "name_suffix",
            "basic_6": "employment_status",  # Personalstatus
            "basic_7": "title",
            "basic_8": "note",
            "basic_9": "academic_degree",    # Akad. Grad
            "basic_10": "status",
        }

        # Loop over all <th> in that Grunddaten table
        for th in doc.xpath('//table[@summary="Grunddaten zur Veranstaltung"]//th[@id]'):
            field_id = th.get("id")              # e.g. "basic_1"
            key = id_map.get(field_id)
            if not key:
                continue                         # skip columns we don't care about

            # grab the matching <td headers="basic_X">
            td = doc.xpath(f'//td[@headers="{field_id}"]')
            value = td[0].text_content().strip() if td else ""
            details["basic_info"][key] = value

        # Ensure all expected keys are present
        for key in id_map.values():
            details["basic_info"].setdefault(key, "")

        # Extract roles and institutions from the Funktionen table
        function_rows = doc.xpath('//table[@summary="Funktionen"]//tr[position()>1]')
        for row in function_rows:
            cells = row.xpath('.//td')
            if len(cells) >= 2:
                institution = cells[0].xpath('.//a/text()')
                role = cells[1].xpath('.//text()')
                if institution and role:
                    role_info = {
                        "institution": self._clean_text(institution[0]),
                        "role": self._clean_text(role[0])
                    }
                    if cells[0].xpath('.//a/@href'):
                        role_info["institution_url"] = cells[0].xpath('.//a/@href')[0]
                    details["roles"].append(role_info)

        # Extract faculty from the structure tree
        faculty_entry = doc.xpath('//div[contains(@style, "padding-left: 10px")]//a[contains(text(), "Fakultät")]')
        if faculty_entry:
            details["faculty"] = self._clean_text(faculty_entry[0].text_content())

        # Extract courses with deduplication
        course_rows = doc.xpath('//table[@summary="Übersicht über die Zugehörigkeit zu Veranstaltungen"]//tr[position()>1]')
        seen_courses = set()  # Track course combinations to avoid duplicates
        
        for row in course_rows:
            cells = row.xpath('.//td')
            if len(cells) >= 3:
                course_number = self._clean_text(cells[0].text_content())
                course_name = self._clean_text(cells[1].xpath('.//a/text()')[0] if cells[1].xpath('.//a/text()') else cells[1].text_content())
                semester = self._clean_text(cells[2].text_content())
                
                # Create a unique identifier for this course to detect duplicates
                course_key = (course_number, course_name, semester)
                if course_key in seen_courses:
                    logger.debug(f"Skipping duplicate course: {course_key}")
                    continue
                
                seen_courses.add(course_key)
                
                course = {
                    "number": course_number,
                    "name": course_name,
                    "semester": semester
                }
                if cells[1].xpath('.//a/@href'):
                    course["url"] = cells[1].xpath('.//a/@href')[0]
                details["courses"].append(course)

        return details

    def _crawl_role(self, pfid: int) -> list[dict]:
        out = []
        too_many_letters = []
        processed_people = set()  # Track processed people by profile URL to avoid duplicates
        
        # First try single letters
        logger.info(f"Starting to process single letters for role {pfid}")
        # Only process first letter for now
        for ch in tqdm.tqdm(list("abcdefghijklmnopqrstuvwxyzäöüß"), desc="Processing single letters"):
        # for ch in tqdm.tqdm(list("a"), desc="Processing single letters"):
        #     logger.debug(f"Processing letter '{ch}' for function {pfid}")
            
            # first do a quick 10-item check for the 1000+ warning
            if self._too_many(ch, pfid):
                logger.warning(f"[{pfid}] Letter '{ch}' >1000 results → will try two-character combinations")
                too_many_letters.append(ch)
                continue

            # Process all pages for this letter
            page = 0
            total_processed = 0
            while True:
                # Use default RESULTS_PER_PAGE (50) for actual data fetching
                doc = self._fetch_search(ch, pfid, page)
                
                # parse the InfoLeiste count
                info = doc.xpath('//div[@class="InfoLeiste"]')
                count = None
                if info:
                    m = re.search(r"(\d+)\s+Treffer", info[0].text_content())
                    count = int(m.group(1)) if m else None
                    if count:
                        logger.debug(f"Found {count} results for letter '{ch}'")

                # Look for person entries
                entries = doc.xpath('//div[contains(@class, "erg_list_entry")]')
                if not entries:
                    break  # No more results

                # Process each person entry
                current_person = {}
                for entry in entries:
                    label = entry.xpath('.//div[@class="erg_list_label"]/text()')
                    if not label:
                        continue
                        
                    label = label[0].strip()
                    value = entry.xpath('.//text()')
                    value = ' '.join(v.strip() for v in value if v.strip())
                    
                    if label == "Name:":
                        # If we have a previous person, save them
                        if current_person:
                            out.append(current_person)
                            total_processed += 1
                            if total_processed % self.RESULTS_PER_PAGE == 0:
                                logger.info(f"Processed {total_processed} people for letter '{ch}'")
                        current_person = {"name": self._clean_text(value)}
                        
                        # Get the profile URL if available
                        link = entry.xpath('.//a[@class="regular"]/@href')
                        if link:
                            # Handle relative URLs correctly
                            href = link[0]
                            if href.startswith('/'):
                                profile_url = f"https://lsf.verwaltung.uni-muenchen.de{href}"
                            else:
                                profile_url = href
                            
                            # Check if we've already processed this person
                            if profile_url in processed_people:
                                logger.debug(f"Skipping already processed person: {current_person['name']} ({profile_url})")
                                current_person = {}  # Reset to skip this person
                                continue
                            
                            current_person["profile_url"] = profile_url
                            processed_people.add(profile_url)
                            
                            # Fetch and parse the person's detail page
                            try:
                                detail_doc = self._fetch_person_details(href)
                                details = self._extract_person_details(detail_doc)
                                current_person.update(details)
                            except Exception as e:
                                logger.warning(f"Failed to fetch details for person {current_person.get('name', 'Unknown')}: {e}")
                                # Continue processing other people even if one fails
                                
                    elif label == "Dienstadresse:":
                        current_person["address"] = self._clean_text(value)
                    elif label == "E-Mail:":
                        current_person["email"] = self._clean_text(value)
                
                # Don't forget to add the last person
                if current_person:
                    out.append(current_person)
                    total_processed += 1

                # Check if we've processed all results
                if count and total_processed >= count:
                    break
                    
                page += 1
                
            logger.info(f"Completed letter '{ch}': processed {total_processed} people")
        
        # Now try two-character combinations for letters that had too many results
        if too_many_letters:
            logger.info(f"Starting two-character combinations for letters: {', '.join(too_many_letters)}")
            total_combinations = len(too_many_letters) * len("abcdefghijklmnopqrstuvwxyzäöüß")
            with tqdm.tqdm(total=total_combinations, desc="Processing two-letter combinations") as pbar:
                for ch1 in too_many_letters:
                    for ch2 in list("abcdefghijklmnopqrstuvwxyzäöüß"):
                        search = f"{ch1}{ch2}"
                        logger.debug(f"Processing two-letter combination '{search}' for function {pfid}")
                        
                        # Process all pages for this two-letter combination
                        page = 0
                        total_processed = 0
                        while True:
                            # Use default RESULTS_PER_PAGE (50) for actual data fetching
                            doc = self._fetch_search(search, pfid, page)
                            
                            # parse the InfoLeiste count
                            info = doc.xpath('//div[@class="InfoLeiste"]')
                            count = None
                            if info:
                                m = re.search(r"(\d+)\s+Treffer", info[0].text_content())
                                count = int(m.group(1)) if m else None
                                if count:
                                    logger.debug(f"Found {count} results for combination '{search}'")

                            # Look for person entries
                            entries = doc.xpath('//div[contains(@class, "erg_list_entry")]')
                            if not entries:
                                break  # No more results

                            # Process each person entry
                            current_person = {}
                            for entry in entries:
                                label = entry.xpath('.//div[@class="erg_list_label"]/text()')
                                if not label:
                                    continue
                                    
                                label = label[0].strip()
                                value = entry.xpath('.//text()')
                                value = ' '.join(v.strip() for v in value if v.strip())
                                
                                if label == "Name:":
                                    # If we have a previous person, save them
                                    if current_person:
                                        out.append(current_person)
                                        total_processed += 1
                                        if total_processed % self.RESULTS_PER_PAGE == 0:
                                            logger.info(f"Processed {total_processed} people for combination '{search}'")
                                    current_person = {"name": self._clean_text(value)}
                                    
                                    # Get the profile URL if available
                                    link = entry.xpath('.//a[@class="regular"]/@href')
                                    if link:
                                        # Handle relative URLs correctly
                                        href = link[0]
                                        if href.startswith('/'):
                                            profile_url = f"https://lsf.verwaltung.uni-muenchen.de{href}"
                                        else:
                                            profile_url = href
                                        
                                        # Check if we've already processed this person
                                        if profile_url in processed_people:
                                            logger.debug(f"Skipping already processed person: {current_person['name']} ({profile_url})")
                                            current_person = {}  # Reset to skip this person
                                            continue
                                        
                                        current_person["profile_url"] = profile_url
                                        processed_people.add(profile_url)
                                        
                                        # Fetch and parse the person's detail page
                                        try:
                                            detail_doc = self._fetch_person_details(href)
                                            details = self._extract_person_details(detail_doc)
                                            current_person.update(details)
                                        except Exception as e:
                                            logger.warning(f"Failed to fetch details for person {current_person.get('name', 'Unknown')}: {e}")
                                            # Continue processing other people even if one fails
                                            
                                elif label == "Dienstadresse:":
                                    current_person["address"] = self._clean_text(value)
                                elif label == "E-Mail:":
                                    current_person["email"] = self._clean_text(value)
                            
                            # Don't forget to add the last person
                            if current_person:
                                out.append(current_person)
                                total_processed += 1

                            # Check if we've processed all results
                            if count and total_processed >= count:
                                break
                                
                            page += 1
                            
                        logger.info(f"Completed combination '{search}': processed {total_processed} people")
                        pbar.update(1)
            
        # Remove any empty dictionaries that might have been added during duplicate skipping
        out = [person for person in out if person]
        
        logger.info(f"Finished processing role {pfid}: collected {len(out)} people in total")
        logger.info(f"Processed {len(processed_people)} unique people (deduplication applied)")
        return out

    def _fetch_person_details(self, href: str) -> html.HtmlElement:
        """Fetch and parse a person's detail page."""
        if href.startswith('/'):
            url = f"https://lsf.verwaltung.uni-muenchen.de{href}"
        else:
            url = href
            
        try:
            r = self._make_request(url)
            return html.fromstring(r.content)
        except Exception as e:
            logger.error(f"Failed to fetch person details from {url}: {e}")
            raise

    def _too_many(self, letter: str, pfid: int) -> bool:
        doc = self._fetch_search(letter, pfid, 0, per_page=50)
        text_blobs = [p.text_content() for p in doc.xpath("//p")]
        
        for t in text_blobs:
            if "mehr als 1000 Ergebnisse" in t:
                logger.debug(f"Too many (>1000) results for letter '{letter}' and function {pfid}")
                return True
            elif "mehr als 100 Ergebnisse" in t:
                logger.debug(f"Too many (>100) results for letter '{letter}' and function {pfid}")
                return True
        
        return False

    def _fetch_search(self, letter: str, pfid: int, page: int = 0, per_page: int = None) -> html.HtmlElement:
        if per_page is None:
            per_page = self.RESULTS_PER_PAGE
            
        params = {
            "state":                     "wsearchv",
            "search":                    "7",
            "purge":                     "y", 
            "moduleParameter":           "person/person",
            "choice.r_funktion.pfid":    "y",
            "r_funktion.pfid":           str(pfid),
            "personal.nachname":         letter.upper(),
            "P_start":                   str(page * per_page),
            "P_anzahl":                  str(per_page),
            "_form":                     "display"
        }
        url = f"{self.BASE}?{urlencode(params, safe=',')}"
        logger.debug(f"Fetching page {page + 1} with {per_page} results per page")
        logger.debug(f"→ Effective URL: {url}")
        
        try:
            r = self._make_request(url)
            return html.fromstring(r.content)
        except Exception as e:
            logger.error(f"Failed to fetch search results for letter '{letter}', pfid {pfid}: {e}")
            raise
