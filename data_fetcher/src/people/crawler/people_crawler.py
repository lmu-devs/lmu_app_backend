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
from shared.src.enums import AcademicTitleEnum, LSFRoleEnum
from shared.src.core.logging import get_main_fetcher_logger

logger = get_main_fetcher_logger(__name__)


class LSFPersonCrawler:
    BASE = "https://lsf.verwaltung.uni-muenchen.de/qisserver/rds"
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    RESULTS_PER_PAGE = 50
    REQUEST_DELAY = 0  # Increase if you get rate limited
    MAX_RETRIES = 3
    TIMEOUT = 30

    def __init__(self):
        self.session = self._create_session()
        self.functions = self._crawl_functions()
        logger.info(f"Found {len(self.functions)} roles to try.")

    def _create_session(self):
        """Create a requests session with retry strategy."""
        session = requests.Session()

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
                time.sleep(self.REQUEST_DELAY)
                response = self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
                response.raise_for_status()
                return response

            except SSLError as e:
                logger.warning(f"SSL error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)

            except (ConnectionError, Timeout) as e:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)

            except RequestException as e:
                logger.warning(f"Request error on attempt {attempt + 1}/{max_attempts}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(2 ** attempt)

        raise RuntimeError(f"Failed to make request after {max_attempts} attempts")

    def _crawl_functions(self) -> dict[int, str]:
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
            val = opt.get("value", "").strip()
            txt = opt.text_content().strip()
            if val:
                try:
                    funcs[int(val)] = txt
                    logger.debug(f"Role {val}: {txt}")
                except ValueError:
                    logger.debug(f"Skipping non-int role value: {val}")
        return funcs

    def _create_role_info(self, pfid: int, role_name: str) -> dict:
        """Create role information with LSFRole enum mapping."""
        lsf_role = LSFRoleEnum.from_string(role_name)
        return {
            "lsf_role_enum": lsf_role.value,
            "institutions": []
        }

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing extra whitespace and common prefixes."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'^(Name:|Funktion:|Dienstadresse:|E-Mail:|Dienstzimmer:)', '', text)
        return text.strip()

    def _extract_person_details(self, doc: html.HtmlElement) -> dict:
        """Extract detailed information about a person from their detail page."""
        details = {
            "basic_info": {},
            "faculty": None,
            "roles": [],
            "courses": []
        }

        id_map = {
            "basic_1": "last_name",
            "basic_2": "gender",
            "basic_3": "first_name",
            "basic_4": "office_hours",
            "basic_5": "name_suffix",
            "basic_6": "employment_status",
            "basic_7": "title",
            "basic_8": "note",
            "basic_9": "academic_degree",
            "basic_10": "status",
        }

        grunddaten_xpath = '//table[contains(@summary, "Grunddaten")]//th[@id]'
        th_elements = doc.xpath(grunddaten_xpath)
        logger.debug(f"[Crawler] Found {len(th_elements)} <th> elements in Grunddaten table")

        for th in th_elements:
            field_id = th.get("id")
            key = id_map.get(field_id)
            if not key:
                continue
            td = doc.xpath(f'//td[@headers="{field_id}"]')
            value = td[0].text_content().strip() if td else ""
            details["basic_info"][key] = value

        for key in id_map.values():
            details["basic_info"].setdefault(key, "")

        # Funktionen table
        function_rows = doc.xpath('//table[@summary="Funktionen"]//tr[position()>1]')
        logger.debug(f"[Crawler] Found {len(function_rows)} function rows in Funktionen table")
        for row in function_rows:
            cells = row.xpath('.//td')
            if len(cells) >= 2:
                institution_name = cells[0].xpath('.//a/text()')
                role_text = cells[1].xpath('.//text()')
                institution_url = cells[0].xpath('.//a/@href')
                institution_id = None
                institution_data = None
                if institution_name and role_text:
                    role_enum = LSFRoleEnum.from_string(self._clean_text(role_text[0]))
                    institution_obj = {
                        "name": self._clean_text(institution_name[0]),
                        "url": institution_url[0] if institution_url else None,
                        "id": institution_id,
                        "data": institution_data
                    }
                    details["roles"].append({
                        "lsf_role_enum": role_enum.value,
                        "institutions": [institution_obj]
                    })

        # Faculty extraction with fallback
        faculty_entry = doc.xpath('//div[contains(@style, "padding-left")]//a[contains(text(), "Fakultät")]')
        logger.debug(f"[Crawler] Faculty entry matches: {len(faculty_entry)}")
        if faculty_entry:
            details["faculty"] = self._clean_text(faculty_entry[0].text_content())
        else:
            for role in details.get("roles", []):
                for inst in role.get("institutions", []):
                    inst_name = inst.get("name", "")
                    if "Fakultät" in inst_name:
                        details["faculty"] = self._clean_text(inst_name)
                        logger.debug(f"[Crawler] Faculty inferred from institution name: '{details['faculty']}'")
                        break
                if details["faculty"]:
                    break

            if not details["faculty"]:
                generic_fac = doc.xpath('//a[contains(text(), "Fakultät")]')
                if generic_fac:
                    details["faculty"] = self._clean_text(generic_fac[0].text_content())
                    logger.debug(f"[Crawler] Faculty inferred from generic anchor: '{details['faculty']}'")

        if details["faculty"]:
            logger.debug(f"[Crawler] Final faculty value: '{details['faculty']}'")
        else:
            logger.warning("[Crawler] Faculty could not be determined for this person")

        # Courses with deduplication
        course_rows = doc.xpath('//table[@summary="Übersicht über die Zugehörigkeit zu Veranstaltungen"]//tr[position()>1]')
        # logger.debug(f"🎓 [CRAWLER] Found {len(course_rows)} course rows in Veranstaltungen table")
        seen_courses = set()

        for i, row in enumerate(course_rows):
            cells = row.xpath('.//td')
            # logger.debug(f"🎓 [CRAWLER] Row {i+1}: Found {len(cells)} cells")
            if len(cells) >= 3:
                course_number = self._clean_text(cells[0].text_content())
                course_name = self._clean_text(
                    cells[1].xpath('.//a/text()')[0] if cells[1].xpath('.//a/text()') else cells[1].text_content()
                )
                semester = self._clean_text(cells[2].text_content())

                # logger.debug(f"🎓 [CRAWLER] Row {i+1}: number='{course_number}', name='{course_name}', semester='{semester}'")

                course_key = (course_number, course_name, semester)
                if course_key in seen_courses:
                    # logger.debug(f"🎓 [CRAWLER] Skipping duplicate course: {course_key}")
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
                # logger.debug(f"🎓 [CRAWLER] ✅ Added course {i+1}: {course}")
            else:
                pass

        non_empty_basic = {k: v for k, v in details["basic_info"].items() if v}
        logger.debug(f"[Crawler] Extracted non-empty basic_info fields: {list(non_empty_basic.keys())}")

        return details

    def get_character_list(self) -> list[str]:
        """Return list of characters to crawl (a-z)."""
        return [chr(i) for i in range(ord('a'), ord('z') + 1)]

    async def crawl_people_by_role_and_character_async(self, role_id: int, character: str) -> list[dict]:
        """
        Crawl people for a specific role and character with proper pagination and two-letter fallback.
        """
        try:
            people = []

            # First attempt single-character exhaustive crawl
            single_people = self._crawl_by_letter_or_prefix(role_id, character)
            people.extend(single_people)

            # If too many results on the single character, fallback to two-letter prefixes
            if self._too_many(character, role_id):
                logger.info(f"Letter '{character}' had too many results; trying two-letter prefixes")
                extended_chars = list("abcdefghijklmnopqrstuvwxyzäöüß")
                for second in extended_chars:
                    prefix = f"{character}{second}"
                    prefix_people = self._crawl_by_letter_or_prefix(role_id, prefix)
                    people.extend(prefix_people)

            logger.debug(f"Crawled total {len(people)} people for role {role_id} and character/prefix '{character}'")
            return people

        except Exception as e:
            logger.error(f"Error crawling people for character '{character}' and role {role_id}: {e}")
            return []

    def _crawl_by_letter_or_prefix(self, role_id: int, search: str) -> list[dict]:
        """Exhaustively crawl all pages for the given search string (letter or prefix)."""
        out = []
        page = 0
        total_processed = 0

        while True:
            try:
                doc = self._fetch_search(search, role_id, page)
            except Exception as e:
                logger.warning(f"Failed fetching search '{search}' page {page}: {e}")
                break

            # Parse total count if present
            count = None
            info = doc.xpath('//div[contains(@class,"InfoLeiste")]')
            if info:
                m = re.search(r"(\d+)\s+Treffer", info[0].text_content())
                if m:
                    count = int(m.group(1))
                    logger.debug(f"Search '{search}': total {count} according to InfoLeiste")

            page_people = self._extract_people_from_page(doc)
            if not page_people:
                break

            out.extend(page_people)
            total_processed += len(page_people)

            if count and total_processed >= count:
                break

            page += 1
            if page > 200:  # safety cap
                logger.warning(f"Hit page cap for search '{search}' after {page} pages")
                break

        logger.info(f"Completed search '{search}' for role {role_id}: collected {len(out)} people")
        return out

    def _extract_people_from_page(self, doc: html.HtmlElement) -> list[dict]:
        """Extract people data from a search results page."""
        people = []

        try:
            person_links = doc.xpath('//a[contains(@href, "personal.nachname")]')

            for link in person_links:
                try:
                    name = link.text_content().strip()
                    href = link.get('href')

                    if name and href:
                        detail_doc = self._fetch_person_details(href)
                        person_details = self._extract_person_details(detail_doc)
                        person_details['name'] = name
                        person_details['href'] = href
                        people.append(person_details)

                except Exception as e:
                    logger.warning(f"Failed to extract person from link: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting people from page: {e}")

        return people

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