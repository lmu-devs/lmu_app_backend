import codecs
from collections import defaultdict
from typing import Any, Optional
import concurrent.futures
from requests.sessions import Session
import requests
import re
import time
from datetime import time as Time, date as Date, datetime as dt
from urllib.parse import urlparse, parse_qs, unquote
from lxml import html
import random
import logging


from shared.src.core.logging import get_classes_logger
from shared.src.enums.classes_enum import (
    LectureStartTypeEnum,
    SemesterTypeEnum,
)
from shared.src.enums.weekday_enum import WeekdayEnum
from ..models.lecture import (
    AdditionInformation,
    AssociatedClass,
    AssociatedExam,
    AssociatedProgram,
    AssociatedTutorial,
    ClassBaseInfo,
    ClassMaterial,
    ClassSession,
    EnrollmentDeadline,
    ExamInformation,
    Institution,
    Lecture,
    Person,
)


class LSFCrawler:
    """Crawler for the LSF (Lehre, Studium, Forschung) system of LMU Munich."""

    def __init__(self) -> None:
        self.logger = get_classes_logger(__name__)
        self.workers = 4
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
        ]
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
            """Create session with consistent headers for its lifetime."""
            session = requests.Session()
            session.headers.update(self.get_random_header())
            return session

    def get_random_header(self) -> dict[str, str]:
        """Get a random header for the session."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,en-GB;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }


    def crawl_all_lectures(self, year: int, semester_type: SemesterTypeEnum) -> list[Lecture]:
        """Crawl all lectures for a given year and semester type sequentially."""
        self._set_crawling_parameters(year, semester_type)
        lecture_urls = self._crawl_all_lecture_urls_sequentially()
        return self._crawl_all_lectures_sequentially(lecture_urls)

    def crawl_all_lectures_parallel(self, year: int, semester_type: SemesterTypeEnum) -> list[Lecture]:
        """Crawl all lectures for a given year and semester type in parallel."""
        self._set_crawling_parameters(year, semester_type)
        lecture_urls = self._crawl_lecture_urls_in_parallel()[:100]
        return self._crawl_all_lectures_in_parallel(lecture_urls)

    def _set_crawling_parameters(self, year: int, semester_type: SemesterTypeEnum) -> None:
        """Set the year and semester type for the crawling session."""
        self.year = year
        self.semester_type = semester_type

    def _crawl_all_lecture_urls_sequentially(self) -> list[tuple[str, str]]:
        """Crawl all lecture URLs sequentially."""
        lecture_urls = []
        self.logger.info("Getting class type ids...")
        class_type_ids = self._get_all_available_class_type_ids()

        for index, type_id in enumerate(class_type_ids):
            self.logger.info(f"Fetching class urls: ({index + 1}/{len(class_type_ids)})")
            lecture_urls += self._get_lecture_urls_for_class_type(type_id)

        return lecture_urls

    def crawl_all_lecture_urls_sequentially(self, year: int, semester_type: SemesterTypeEnum) -> list[tuple[str, str]]:
        """Crawl all lecture URLs sequentially."""
        lecture_urls = []
        self.logger.info("Getting class type ids...")
        class_type_ids = self._get_all_available_class_type_ids()
        self._set_crawling_parameters(year, semester_type)

        for index, type_id in enumerate(class_type_ids):
            self.logger.info(f"Fetching class urls: ({index + 1}/{len(class_type_ids)})")
            lecture_urls += self._get_lecture_urls_for_class_type(type_id)

        return lecture_urls

    def _crawl_lecture_urls_in_parallel(self) -> list[tuple[str, str]]:
        """Collect all lecture URLs in parallel using ThreadPoolExecutor."""
        class_types = self._get_all_available_class_types_with_names()
        all_lecture_tuples: list[tuple[str, str]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self._get_lecture_urls_for_class_type, type_id): type_id
                for type_id in class_types.keys()
            }
            for index, future in enumerate(concurrent.futures.as_completed(futures)):
                self.logger.info(f"Fetching class urls: ({index + 1}/{len(futures)})")
                all_lecture_tuples.extend(future.result())

        return all_lecture_tuples

    def _get_lecture_urls_for_class_type(self, type_id: int) -> list[tuple[str, str]]:
        """Get lecture URLs for a specific class type, handling large result sets."""
        if self._does_class_type_have_too_many_results(type_id):
            return self._get_lecture_urls_with_alphabetical_splitting(type_id)
        else:
            return self._get_lecture_urls_with_search_filter("", type_id)

    def _get_lecture_urls_with_alphabetical_splitting(self, type_id: int) -> list[tuple[str, str]]:
        """Split large class type results by searching with each letter of the alphabet."""
        lectures: list[tuple[str, str]] = []
        german_chars = list("abcdefghijklmnopqrstuvwxyzäöüß")

        for ch in german_chars:
            lectures += self._get_lecture_urls_with_search_filter(ch, type_id)

        return lectures

    def _crawl_all_lectures_sequentially(self, urls: list[tuple[str, str]]) -> list[Lecture]:
        """Process all lecture URLs sequentially to build Lecture objects."""
        lectures = []

        for index, url in enumerate(urls):
            self.logger.info(f"Processing lecture({index+1}/{len(urls)}): {url}")
            lectures += [self._build_complete_lecture_object(url)]

        return lectures

    def _crawl_all_lectures_in_parallel(self, lecture_urls: list[tuple[str, str]]) -> list[Lecture]:
        """Process all lecture URLs in parallel to build Lecture objects."""
        lectures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self._build_complete_lecture_object, name_url): name_url for name_url in lecture_urls
            }
            for index, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    lecture = future.result()
                    lectures.append(lecture)
                    self.logger.info(f"Processed lecture({index+1}/{len(futures)}): {lecture.title} ({lecture.publish_id})")
                except Exception as e:
                    self.logger.error(f"❌ Error while building lecture: {e}")

        return lectures

    def _build_complete_lecture_object(self, name_url: tuple[str, str]) -> Lecture:
        """Build a complete lecture object from a name and URL."""
        name, url = name_url
        response_bytes = self._make_safe_http_request(url)

        return Lecture.from_tuple(
            (name, url, self._extract_navigation_tree_paths(response_bytes)),
            self._extract_class_base_information(response_bytes),
            self._extract_additional_lecture_information(response_bytes),
            self._extract_enrollment_deadline_information(response_bytes),
            self._extract_associated_study_programs(response_bytes),
            self._extract_class_material_information(response_bytes),
            self._extract_associated_exam_information(response_bytes),
            self._extract_detailed_exam_information(response_bytes),
            self._extract_class_session_schedules(response_bytes),
            self._extract_associated_tutorial_information(response_bytes),
            self._extract_associated_class_information(response_bytes),
            self._extract_responsible_persons_from_lecture_page(response_bytes)
        )

    def build_complete_lecture_object(self, name: str, url: str) -> Lecture:
        """Build a complete lecture object from a name and URL."""
        response_bytes = self._make_safe_http_request(url)

        return Lecture.from_tuple(
            (name, url, self._extract_navigation_tree_paths(response_bytes)),
            self._extract_class_base_information(response_bytes),
            self._extract_additional_lecture_information(response_bytes),
            self._extract_enrollment_deadline_information(response_bytes),
            self._extract_associated_study_programs(response_bytes),
            self._extract_class_material_information(response_bytes),
            self._extract_associated_exam_information(response_bytes),
            self._extract_detailed_exam_information(response_bytes),
            self._extract_class_session_schedules(response_bytes),
            self._extract_associated_tutorial_information(response_bytes),
            self._extract_associated_class_information(response_bytes),
            self._extract_responsible_persons_from_lecture_page(response_bytes)
        )

    def _does_class_type_have_too_many_results(self, class_type: int) -> bool:
        """Check if a class type returns too many results (>1000) requiring splitting."""
        error_message = "Ihre Anfrage lieferte mehr als 1000 Ergebnisse"
        response_bytes = self._make_safe_http_request(self._build_class_search_url("", class_type))
        tree = html.fromstring(response_bytes)
        p_tags = tree.xpath("//p")

        return any(error_message in p.text_content() for p in p_tags)

    def _make_safe_http_request(self, url: str, timeout: float = 10, retries: int = 10) -> bytes:
        """Make HTTP request with retry logic and error handling."""
        for attempt in range(1, retries + 1):
            try:
                response = self.session.get(url, headers=self.get_random_header(), timeout=timeout)
                response.raise_for_status()
                return response.content
            except Exception as e:
                self.logger.error(f"[Retry {attempt}/{retries}] Error fetching {url}: {e}")
                if attempt < retries:
                    time.sleep(2**attempt)
                else:
                    self.logger.fatal(f"[FAIL] Giving up on {url}")

        self.logger.fatal(f"Failed to fetch {url} after {retries} retries")

    def _get_lecture_urls_with_search_filter(self, search_text: str, class_type: int) -> list[tuple[str, str]]:
        """Extract lecture URLs from search results for a given search filter."""
        request_bytes = self._make_safe_http_request(self._build_class_search_url(search_text, class_type))
        if self._is_invalid_semester(request_bytes):
            return []

        tree = html.fromstring(request_bytes)

        classes = tree.xpath('//a[@class="regular" and @title]')
        info = tree.xpath('//div[@class="InfoLeiste"]')

        expected_count = self._extract_result_count_from_info_bar(info)
        assert len(classes) == expected_count, "Mismatch in expected class count"

        return [
            (self._clean_and_normalize_string(c.text), self._clean_and_normalize_string(c.get("href"))) for c in classes
        ]

    def _is_invalid_semester(self, response_bytes: bytes) -> bool:
        return "Ungültiges Semester" in response_bytes.decode()

    def _extract_result_count_from_info_bar(self, info: Any) -> int:
        """Parse the class count from the info section of the HTML."""
        class_count = re.search(r"(\d+)\s+Treffer", info[0].text)
        assert class_count, f"Error parsing class count: {info}"
        return int(class_count.group(1))

    def _build_class_search_url(self, search_text: str, class_type: int) -> str:
        """Build URL for searching classes with specific filters."""
        semester_type = 1 if self.semester_type.value == "SOSE" else 2

        return (
            "https://lsf.verwaltung.uni-muenchen.de"
            + "/qisserver/rds?state=wsearchv"
            + "&search=1&subdir=veranstaltung&choice.veranstaltung.verartid=y&"
            + f"veranstaltung.verartid={class_type}"
            + f"&veranstaltung.dtxt={search_text}"
            + f"&veranstaltung.semester={self.year}{semester_type}"
            + "&P_start=0&P_anzahl=1000&P.sort=&_form=display"
        )

    def _get_all_available_class_type_ids(self) -> list[int]:
        """Get just the class type IDs without names."""
        return list(self._get_all_available_class_types_with_names().keys())

    def _get_all_available_class_types_with_names(self) -> dict[int, str]:
        """Retrieve all available class types with their IDs and names."""
        class_types = {}
        url = self._build_class_types_discovery_url()
        request_bytes = self._make_safe_http_request(url)
        tree = html.fromstring(request_bytes)
        select = tree.get_element_by_id("veranstaltung.verartid")

        for option in select.xpath(".//option"):
            class_id = option.get("value")
            class_type = option.text_content().strip()
            if class_id:
                class_types[class_id] = class_type

        return class_types

    def _build_class_types_discovery_url(self) -> str:
        """Build the URL for discovering available class types."""
        return (
            "https://lsf.verwaltung.uni-muenchen.de/qisserver/"
            + "rds?state=change&type=5&moduleParameter="
            + "veranstaltungSearch&nextdir=change&next="
            + "search.vm&subdir=veranstaltung&_form=display&"
            + "function=search&clean=y&category=veranstaltung.search"
        )

    def _extract_navigation_tree_paths(self, response_bytes: bytes) -> Optional[list[list[str]]]:
        """Extract hierarchical navigation paths from the lecture page."""
        tree = html.fromstring(response_bytes)
        navigation_nodes = tree.xpath("//div[contains(@style, 'padding-left')]/a")
        paths = []
        indentation_stack = []

        for node in navigation_nodes:
            parent_div = node.getparent()
            style_attribute = parent_div.attrib.get("style", "")
            text_content = self._clean_and_normalize_string(node.text_content().strip())

            try:
                indentation_level = int(style_attribute.split("padding-left:")[1].split("px")[0].strip())
            except Exception:
                continue

            while indentation_stack and indentation_stack[-1][0] >= indentation_level:
                indentation_stack.pop()

            indentation_stack.append((indentation_level, text_content))

            if parent_div.xpath(".//span[@class='warnung']"):
                current_path = [text for _, text in indentation_stack]
                paths.append(current_path)
        return paths if paths else None

    def _extract_class_base_information(self, response_bytes: bytes) -> ClassBaseInfo:
        """Extract basic class information including persons and institutions."""
        base_info_dict: dict[str, Any] = {
            "institutions": self._extract_associated_institutions_from_lecture_page(response_bytes),
        }
        return ClassBaseInfo(**(base_info_dict | self._extract_basic_lecture_data_from_html(response_bytes)))

    def _extract_responsible_persons_from_lecture_page(self, html_text: Any) -> Optional[list[Person]]:
        """Extract responsible persons/lecturers from the lecture page."""
        tree = html.fromstring(html_text)
        persons_table = tree.xpath('//table[@summary="Verantwortliche Dozenten"]')
        if len(persons_table) == 0:
            return None

        persons = []
        for row in persons_table:
            if len(row_entrys := row.xpath(".//td")) == 0:
                continue
            person_raw = row_entrys[0].text_content().strip()

            if person_raw == "keine öffentliche Person":
                continue
            persons.append(Person.from_str(self._clean_and_normalize_string(person_raw)))

        return persons if len(persons) > 0 else None

    def _extract_associated_institutions_from_lecture_page(
        self,
        html_content: Any,
    ) -> Optional[list[Institution]]:
        """Extract associated institutions from the lecture page."""
        tree = html.fromstring(html_content)
        rows = tree.xpath("//table[@summary='Übersicht über die zugehörigen Einrichtungen']//tr")

        institutions = []
        for row in rows:
            link = row.xpath(".//a[@class='regular']")
            if link:
                name = self._clean_and_normalize_string(link[0].text_content())
                institutions.append(Institution(name=name))

        return institutions

    def _extract_basic_lecture_data_from_html(self, html_text: Any) -> dict[str, Optional[Any]]:
        """Extract basic data from the lecture's 'Grunddaten' table."""
        base_info_dict: dict[str, Optional[Any]] = {
            "Weitere Links": "",
            "Sigel": "",
        }

        tree = html.fromstring(html_text)
        base_info_table = tree.xpath('//table[caption[text()="Grunddaten"]]')[0]

        for row in base_info_table.xpath(".//tr"):
            headers = row.xpath(".//th")
            values = row.xpath(".//td")

            for header, data in zip(headers, values):
                key = str(header.text_content().strip())
                value = self._clean_and_normalize_string(data.text_content())

                if key == "Weitere Links":
                    base_info_dict[key] = self._parse_course_information_url(data)
                    continue
                if key == "SWS":
                    base_info_dict[key] = self._parse_float(value)
                    continue
                if key == "Max. Teilnehmer/-innen":
                    base_info_dict[key] = self._parse_int(value)

                base_info_dict[key] = None if value == "" else value

        return base_info_dict

    def _extract_associated_tutorial_information(self, response_bytes: bytes) -> Optional[list[AssociatedTutorial]]:
        """Extract information about associated tutorials."""
        tutorial_data = self._extract_data_from_table_with_summary(response_bytes, "Zugehörige Übungen")

        if not tutorial_data:
            return None

        for tutorial in tutorial_data:
            number = tutorial["Nr."]
            hours = tutorial["SWS"]
            tutorial["number"] = number if number else None
            tutorial["weekly_hours"] = float(hours) if hours else None

        return [AssociatedTutorial(**table) for table in tutorial_data]

    def _extract_associated_class_information(self, response_bytes: bytes) -> Optional[list[AssociatedClass]]:
        """Extract information about associated classes."""
        class_data = self._extract_data_from_table_with_summary(response_bytes, "Zugehörige Veranstaltungen")

        if not class_data:
            return None

        for class_info in class_data:
            number = class_info["Nr."]
            hours = class_info["SWS"]
            class_info["number"] = number if number else None
            class_info["weekly_hours"] = float(hours) if hours else None

        return [AssociatedClass(**table) for table in class_data]

    def _extract_enrollment_deadline_information(self, response_bytes: bytes) -> Optional[EnrollmentDeadline]:
        """Extract enrollment deadline information with program-specific and general deadlines."""
        tree = html.fromstring(response_bytes)
        deadline_tables = tree.xpath(
            "//table[@summary='Übersicht über die zugehörigen Belegfristen'" + "and not(ancestor::table)]"
        )

        if len(deadline_tables) != 1:
            return None

        table_rows = deadline_tables[0].xpath("./tr")
        program_specific_rows = []
        general_deadline_rows = []
        current_section = None

        for row in table_rows:
            if row.xpath("./td[@colspan]"):
                text = row.text_content().strip().lower()
                if "studiengangsbezogene fristen" in text:
                    current_section = "program"
                elif "sonstige fristen" in text:
                    current_section = "other"
                else:
                    current_section = None
                continue

            row_html = self._clean_and_normalize_string(str(html.tostring(row, encoding="unicode")))

            if current_section == "program":
                program_specific_rows.append(row_html)
            elif current_section == "other":
                general_deadline_rows.append(row_html)

        return EnrollmentDeadline(
            program_associated_deadline=self._wrap_rows_in_table_tags(program_specific_rows),
            other_deadlines=self._wrap_rows_in_table_tags(general_deadline_rows),
        )

    def _wrap_rows_in_table_tags(self, rows: list[str]) -> Optional[str]:
        """Wrap table rows in table tags if rows exist."""
        if not rows:
            return None

        rows_content = "\n".join(rows)
        return f"<table>{rows_content}</table>"

    def _extract_detailed_exam_information(self, response_bytes: bytes) -> Optional[list[ExamInformation]]:
        """Extract detailed exam information including registration periods."""
        exam_data = self._extract_data_from_table_with_summary(response_bytes, "Übersicht über die zugehörigen PORG")

        if not exam_data:
            return None

        for exam in exam_data:
            registration_duration = exam["Anmeldungszeitraum"]
            exam["registration_start"] = (
                self._parse_duration_start(registration_duration) if registration_duration else None
            )
            exam["registration_end"] = (
                self._parse_duration_end(registration_duration) if registration_duration else None
            )
            exam["ECTS"] = self._parse_ects_from_text(exam["ECTS"]) if exam["ECTS"] else None
            exam["Datum"] = dt.strptime(exam["Datum"], "%d.%m.%Y") if exam["Datum"] else None

        return [ExamInformation(**data) for data in exam_data]

    def _extract_additional_lecture_information(self, response_bytes: bytes) -> Optional[AdditionInformation]:
        """Extract additional information from the 'Weitere Angaben' table."""
        tree = html.fromstring(response_bytes)
        additional_info_tables = tree.xpath(
            "//table[@summary='Weitere Angaben zur Veranstaltung'" + "and not(ancestor::table)]"
        )

        additional_data: defaultdict = defaultdict(lambda: None)

        if not additional_info_tables:
            return None

        assert len(additional_info_tables) == 1
        additional_info_table = additional_info_tables[0]

        for table_row in additional_info_table.xpath(".//tr"):
            header_cells = table_row.xpath("./th")
            data_cells = table_row.xpath("./td")
            if header_cells and data_cells:
                key = str(header_cells[0].text_content().strip())
                if len(data_cells[0]):
                    inner_html = "".join(
                        self._clean_and_normalize_string(str(html.tostring(child, encoding="unicode")))
                        for child in data_cells[0]
                    )
                else:
                    inner_html = self._clean_and_normalize_string(str(data_cells[0].text_content().strip()))

                additional_data[key] = inner_html

        return AdditionInformation(**additional_data)

    def _extract_data_from_table_with_summary(self, response_bytes: bytes, summary: str) -> Optional[list[dict]]:
        """Generic method to extract tabular data based on table summary attribute."""
        tree = html.fromstring(response_bytes)
        matching_tables = tree.xpath(f"//table[@summary='{summary}']")
        table_content = []

        if len(matching_tables) == 0:
            return None

        for table in matching_tables:
            column_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            for table_row in table.xpath(".//tr[position()>1]"):
                cell_values = [
                    (
                        cleaned_data
                        if (
                            (cleaned_data := self._clean_and_normalize_string(td.text_content())) != ""
                            and cleaned_data != "-"
                        )
                        else None
                    )
                    for td in table_row.xpath("td")
                ]
                table_content.append(dict(zip(column_headers, cell_values)))

        return table_content

    def _extract_associated_exam_information(self, response_bytes: bytes) -> Optional[list[AssociatedExam]]:
        """Extract information about exams associated with the lecture."""
        tree = html.fromstring(response_bytes)
        exam_tables = tree.xpath("//table[@summary=" + "'Übersicht über die zugehörigen Prüfungen']")

        if len(exam_tables) == 0:
            return None

        exams = []
        for table in exam_tables:
            column_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            table_rows = []

            for table_row in table.xpath(".//tr[position()>1]"):
                cell_values = [
                    (data if ((data := self._clean_and_normalize_string(td.text_content())) != "") else None)
                    for td in table_row.xpath("td")
                ]
                row_data = dict(zip(column_headers, cell_values))
                table_rows.append(row_data)

            exams += [
                AssociatedExam(
                    module_name=self._remove_ects_from_text(row["Modul"]),
                    program_name=row["Stg"],
                    ects=self._parse_ects_from_text(row["ECTS"] or "" + row["Modul"] or ""),
                    module_classification=row["KzFa"],
                    degree=row["Abschl"],
                    module_id=row["Modulnr"],
                    exam_id=row["Pnr"],
                    po_version=row["Version"],
                )
                for row in table_rows
            ]

        return exams

    @staticmethod
    def _remove_ects_from_text(text: str) -> str:
        """Remove ECTS credits from a string, expecting a format like '5 ECTS'."""
        return re.sub(r"\s*\(?\d+\s*ECTS\)?", "", text).strip()

    @staticmethod
    def _parse_int(raw_int: str) -> Optional[int]:
        """Parse an integer from a string, returning None if parsing fails."""
        try:
            return int(raw_int)
        except Exception:
            return None

    @staticmethod
    def _parse_float(raw_float: str) -> Optional[float]:
        """Parse a float from a string, returning None if parsing fails."""
        try:
            return float(raw_float)
        except Exception:
            return None

    @staticmethod
    def _parse_ects_from_text(text: str) -> Optional[int]:
        """Extract ECTS credits from a string, expecting a format like '5 ECTS'."""
        match = re.search(r"(\d+)\s*ECTS", text)
        if match:
            return int(match.group(1))
        return None

    def _extract_class_material_information(self, response_bytes: bytes) -> Optional[list[ClassMaterial]]:
        """Extract information about class materials and their validity periods."""
        tree = html.fromstring(response_bytes)
        material_tables = tree.xpath("//table[@summary=" + "'Übersicht über die zugehörigen Medien oder so ähnlich']")

        if len(material_tables) == 0:
            return None

        material = []
        for table in material_tables:
            columns_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            table_rows = []

            for table_row in table.xpath(".//tr[position()>1]"):
                cells = [
                    (data if ((data := self._clean_and_normalize_string(td.text_content())) != "") else None)
                    for td in table_row.xpath("td")
                ]
                row_data = dict(zip(columns_headers, cells))
                table_rows.append(row_data)

            material += [
                ClassMaterial(
                    valid_from=(dt.strptime(row["gültig von"], "%d.%m.%Y").date() if row["gültig von"] else None),
                    valid_to=(dt.strptime(row["gültig bis"], "%d.%m.%Y").date() if row["gültig bis"] else None),
                    file_name=row["Dateiname"],
                    description=row["Beschreibung"],
                )
                for row in table_rows
            ]

        return material

    def _extract_associated_study_programs(self, response_bytes: bytes) -> Optional[list[AssociatedProgram]]:
        """Extract information about study programs associated with the lecture."""
        tree = html.fromstring(response_bytes)
        program_tables = tree.xpath("//table[@summary='Übersicht über die zugehörigen Studiengänge']")

        if len(program_tables) == 0:
            return None

        programs = []
        for table in program_tables:
            column_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            table_rows = []

            for table_row in table.xpath(".//tr[position()>1]"):
                cell_values = [self._clean_and_normalize_string(td.text_content()) for td in table_row.xpath("td")]
                row_data = dict(zip(column_headers, cell_values))
                table_rows.append(row_data)

            programs += [
                AssociatedProgram(
                    program_name=row["Studiengang"],
                    ects=self._parse_int(row["ECTS"].split(" ")[0]),
                    degree=row["Abschluss"],
                    module_classification=row["KzFa"],
                )
                for row in table_rows
            ]

        return programs

    def _extract_class_session_schedules(self, response_bytes: bytes) -> Optional[list[ClassSession]]:
        """Extract class session schedules from the response bytes."""
        tree = html.fromstring(response_bytes)
        session_table = tree.xpath("//table[@summary='Übersicht über alle Veranstaltungstermine']")

        if len(session_table) == 0:
            return None

        sessions = []
        for table in session_table:
            column_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            table_caption = c[0] if (c := table.xpath(".//caption/text()")) else None
            table_rows = []

            for table_row in table.xpath(".//tr[position()>1]"):
                cells = [self._clean_and_normalize_string(td.text_content()) for td in table_row.xpath("td")]
                row_data = dict(zip(column_headers, cells))
                table_rows.append(row_data)

            sessions += [
                ClassSession(
                    caption=table_caption,
                    weekday=self._parse_weekday(row["Tag"]),
                    starting_time=self._extract_start_time(row["Zeit"]),
                    ending_time=self._extract_end_time(row["Zeit"]),
                    timing_type=self._extract_time_type(row["Zeit"]),
                    rythm=row["Rhythmus"] or None,
                    duration_start=self._parse_duration_start(row["Dauer"]),
                    duration_end=self._parse_duration_end(row["Dauer"]),
                    room=self._clean_room_name(row["Raum"]),
                    lecturer=row["Lehrperson"] or None,
                    remark=row["Bemerkung"] or None,
                    cancelled_dates=row["fällt aus am"] or None,
                )
                for row in table_rows
            ]

        return sessions

    @staticmethod
    def _clean_room_name(room: str) -> Optional[str]:
        """Clean and normalize room names, removing 'Geschossplan' suffix."""
        if room == "":
            return None
        return re.sub(r"\s+Geschossplan", "", room)

    @staticmethod
    def _extract_times(time_str: str) -> list[str]:
        """Extract time points from a string, expecting formats like "HH:MM"."""
        parts = time_str.split()
        time_regex = re.compile(r"\d{1,2}:\d{2}")
        times = [part for part in parts if time_regex.match(part)]
        return times

    @staticmethod
    def _extract_dates(date_str) -> list[str]:
        """Extract dates from a string, expecting formats like "DD.MM.YYYY"."""
        parts = date_str.split()
        date_regex = re.compile(r"\d{2}\.\d{2}\.\d{4}")
        dates = [part for part in parts if date_regex.match(part)]
        return dates

    def _parse_duration_end(self, time: str) -> Optional[Date]:
        """Parse the end date from a time string, expecting a format like "01.01.2023 - 31.12.2023"."""
        if len(dates := self._extract_dates(time)) < 2:
            return None
        end = dates[1]
        return dt.strptime(end, "%d.%m.%Y").date()

    def _parse_duration_start(self, time: str) -> Optional[Date]:
        """Parse the start date from a time string, expecting a format like "01.01.2023 - 31.12.2023"."""
        if len(dates := self._extract_dates(time)) < 1:
            return None
        start = dates[0]
        return dt.strptime(start, "%d.%m.%Y").date()

    @staticmethod
    def _extract_time_type(time: str) -> Optional[LectureStartTypeEnum]:
        """Extract the type of lecture start from a time string."""
        if "s.t." in time:
            return LectureStartTypeEnum.SINE_TEMPORE
        if "c.t." in time:
            return LectureStartTypeEnum.CUM_TEMPORE
        return None

    @staticmethod
    def _convert_midnight(time: str) -> str:
        """Convert "24:00" to "00:00" for midnight representation."""
        return "00:00" if time == "24:00" else time

    def _extract_end_time(self, time: str) -> Optional[Time]:
        """Extract the end time from a time string, expecting formats like "HH:MM - HH:MM"."""
        if len(time_points := self._extract_times(time)) < 2:
            return None
        end_time = self._convert_midnight(time_points[1])
        return dt.strptime(end_time, "%H:%M").time()

    def _extract_start_time(self, time: str) -> Optional[Time]:
        """Extract the start time from a time string, expecting formats like "HH:MM - HH:MM"."""
        if len(time_points := self._extract_times(time)) < 1:
            return None
        start_time = self._convert_midnight(time_points[0])
        return dt.strptime(start_time, "%H:%M").time()

    @staticmethod
    def _parse_weekday(day: str) -> Optional[WeekdayEnum]:
        """Parse a weekday string into a WeekdayEnum value."""
        mapping = {
            "Mo.": WeekdayEnum.MONDAY,
            "Di.": WeekdayEnum.TUESDAY,
            "Mi.": WeekdayEnum.WEDNESDAY,
            "Do.": WeekdayEnum.THURSDAY,
            "Fr.": WeekdayEnum.FRIDAY,
            "Sa.": WeekdayEnum.SATURDAY,
            "So.": WeekdayEnum.SUNDAY,
        }
        return mapping[day] if day in mapping else None

    def _parse_course_information_url(self, data) -> Optional[str]:
        """Parse the course information URL from the lecture page."""
        link = data.xpath(".//a[contains(text(), 'Course Information')]/@href")

        if not link:
            return None

        raw_href = link[0]
        parsed = urlparse(raw_href)
        query = parse_qs(parsed.query)

        if "destination" in query:
            final_url = unquote(query["destination"][0])
            return final_url
        else:
            return raw_href

    @staticmethod
    def _clean_and_normalize_string(raw: str) -> str:
        """Clean and normalize a string by removing escape characters and extra whitespace."""
        unescaped = codecs.decode(raw, "unicode_escape").encode("latin1").decode("utf-8")
        return re.sub(r"\s+", " ", unescaped).strip()


def main() -> None:
    logger = logging.getLogger(__name__)
    crawler = LSFCrawler()
    print([l.to_dict() for l in crawler.crawl_all_lectures_parallel(2025, SemesterTypeEnum.SUMMER_SEMESTER)])


if __name__ == "__main__":
    main()
