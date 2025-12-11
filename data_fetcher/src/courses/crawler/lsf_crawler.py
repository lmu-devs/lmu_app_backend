import codecs
import concurrent.futures
import logging
import random
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date as Date
from datetime import datetime as dt
from datetime import time as Time
from typing import Any, Iterator, Optional
from urllib.parse import parse_qs, unquote, urlparse

import requests
from lxml import html

from shared.src.core.logging import get_course_logger
from shared.src.enums.courses_enums import CourseStartTypeEnum, SemesterTypeEnum
from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.models.course import (
    AdditionInformation,
    AssociatedClass,
    AssociatedExam,
    AssociatedProgram,
    AssociatedTutorial,
    Course,
    CourseBaseInfo,
    CourseMaterial,
    CourseSession,
    EnrollmentDeadline,
    ExamInformation,
    Institution,
    Person,
)
from shared.utils.html_utils import html_to_markdown


class LSFCrawler:
    """Crawler for the LSF (Lehre, Studium, Forschung) system of LMU Munich."""

    def __init__(self) -> None:
        self.logger: logging.Logger = get_course_logger(__name__)
        self.workers: int = 4
        self.user_agents: list[str] = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.207 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        ]
        self.session: requests.Session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with consistent headers for its lifetime."""
        session = requests.Session()
        session.headers.update(self.get_random_header())
        return session

    def get_random_header(self) -> dict[str, str]:
        """Get a random header for the session."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,en-GB;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

    def build_set_session_semester_url(self, year: int, semester_type: SemesterTypeEnum) -> str:
        semester_text = "Sommersemester" if semester_type == SemesterTypeEnum.SUMMER_SEMESTER else "Wintersemester"
        term_id = 1 if semester_type.value == "SOSE" else 2
        semester_text_year = f"{year}" if term_id == 1 else f"{year}%2F{year + 1}"
        semester_id = f"{year}{term_id}"
        return (
            "https://lsf.verwaltung.uni-muenchen.de/qisserver"
            + f"/rds?state=user&type=0&k_semester.semid={semester_id}"
            + f"&idcol=k_semester.semid&idval={semester_id}"
            + f"&purge=n&getglobal=semester&text={semester_text}+{semester_text_year}"
        )

    def crawl_all_courses(self, year: int, semester_type: SemesterTypeEnum) -> list[Course]:
        """Crawl all courses for a given year and semester type sequentially."""
        self.set_crawling_parameters(year, semester_type)
        course_urls = self._crawl_all_course_urls_sequentially()
        return self._crawl_all_courses_sequentially(course_urls)

    def crawl_all_courses_parallel(self, year: int, semester_type: SemesterTypeEnum) -> list[Course]:
        """Crawl all courses for a given year and semester type in parallel."""
        self.set_crawling_parameters(year, semester_type)
        course_urls = self._crawl_course_urls_in_parallel()
        return self._crawl_all_courses_in_parallel(course_urls)

    def set_crawling_parameters(self, year: int, semester_type: SemesterTypeEnum) -> None:
        """Set the year and semester type for the crawling session."""
        self.year = year
        self.semester_type = semester_type
        self._set_semester_in_lsf()

    def _set_semester_in_lsf(self):
        """Set the semester in the LSF session."""
        set_session_url = self.build_set_session_semester_url(self.year, self.semester_type)
        _ = self._make_safe_http_request(set_session_url)

    def _crawl_all_course_urls_sequentially(self) -> list[tuple[str, str]]:
        """Crawl all course URLs sequentially."""
        course_urls = []
        self.logger.info("Getting course type ids...")
        course_type_ids = self._get_all_available_course_type_ids()

        for index, type_id in enumerate(course_type_ids):
            self.logger.info(f"Fetching course urls: ({index + 1}/{len(course_type_ids)})")
            course_urls += self._get_course_urls_for_course_type(type_id)

        return course_urls

    def crawl_all_course_urls_sequentially(self, year: int, semester_type: SemesterTypeEnum) -> list[tuple[str, str]]:
        """Crawl all course URLs sequentially."""
        course_urls = []
        self.logger.info("Getting course type ids...")
        course_type_ids = self._get_all_available_course_type_ids()
        self.set_crawling_parameters(year, semester_type)

        for index, type_id in enumerate(course_type_ids):
            self.logger.info(f"Fetching course urls: ({index + 1}/{len(course_type_ids)})")
            course_urls += self._get_course_urls_for_course_type(type_id)

        return course_urls

    def _crawl_course_urls_in_parallel(self) -> list[tuple[str, str]]:
        """Collect all course URLs in parallel using ThreadPoolExecutor."""
        course_types = self._get_all_available_course_types_with_names()
        all_course_tuples: list[tuple[str, str]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self._get_course_urls_for_course_type, type_id): type_id
                for type_id in course_types.keys()
            }
            for index, future in enumerate(concurrent.futures.as_completed(futures)):
                self.logger.info(f"Fetching course urls: ({index + 1}/{len(futures)})")
                all_course_tuples.extend(future.result())

        return all_course_tuples

    def _get_course_urls_for_course_type(self, type_id: int) -> list[tuple[str, str]]:
        """Get course URLs for a specific course type, handling large result sets."""
        if self._does_course_type_have_too_many_results(type_id):
            return self._get_course_urls_with_alphabetical_splitting(type_id)
        else:
            return self._get_course_urls_with_search_filter("", type_id)

    def _get_course_urls_with_alphabetical_splitting(self, type_id: int) -> list[tuple[str, str]]:
        """Split large course type results by searching with each letter of the alphabet."""
        courses: list[tuple[str, str]] = []
        german_chars = list("abcdefghijklmnopqrstuvwxyzäöüß")

        for ch in german_chars:
            courses += self._get_course_urls_with_search_filter(ch, type_id)

        return courses

    def _crawl_all_courses_sequentially(self, urls: list[tuple[str, str]]) -> list[Course]:
        """Process all course URLs sequentially to build Course objects."""
        courses = []

        for index, url in enumerate(urls):
            self.logger.info(f"Processing course({index + 1}/{len(urls)}): {url}")
            courses += [self._build_complete_course_object(url)]

        return courses

    def _crawl_all_courses_in_parallel(self, course_urls: list[tuple[str, str]]) -> list[Course]:
        """Process all course URLs in parallel to build Course objects."""
        courses = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self._build_complete_course_object, name_url): name_url for name_url in course_urls
            }
            for index, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    course = future.result()
                    courses.append(course)
                    self.logger.info(
                        f"Fetched course({index + 1}/{len(futures)}): {course.title} ({course.publish_id})"
                    )
                except Exception as e:
                    self.logger.error(f"❌ Error while building course: {e}")

        return courses

    def _build_complete_course_object(self, name_url: tuple[str, str]) -> Course:
        """Build a complete course object from a name and URL."""
        name, url = name_url
        response_bytes = self._make_safe_http_request(url)

        return Course.from_tuple(
            (name, url, self._extract_navigation_tree_paths(response_bytes)),
            self._extract_course_base_information(response_bytes),
            self._extract_additional_course_information(response_bytes),
            self._extract_enrollment_deadline_information(response_bytes),
            self._extract_associated_study_programs(response_bytes),
            self._extract_course_material_information(response_bytes),
            self._extract_associated_exam_information(response_bytes),
            self._extract_detailed_exam_information(response_bytes),
            self._extract_course_session_schedules(response_bytes),
            self._extract_associated_tutorial_information(response_bytes),
            self._extract_associated_course_information(response_bytes),
            self._extract_responsible_persons_from_course_page(response_bytes),
            self._extract_associated_institutions_from_course_page(response_bytes),
        )

    def build_complete_course_object(self, name: str, url: str) -> Course:
        """Build a complete course object from a name and URL."""
        response_bytes = self._make_safe_http_request(url)

        return Course.from_tuple(
            (name, url, self._extract_navigation_tree_paths(response_bytes)),
            self._extract_course_base_information(response_bytes),
            self._extract_additional_course_information(response_bytes),
            self._extract_enrollment_deadline_information(response_bytes),
            self._extract_associated_study_programs(response_bytes),
            self._extract_course_material_information(response_bytes),
            self._extract_associated_exam_information(response_bytes),
            self._extract_detailed_exam_information(response_bytes),
            self._extract_course_session_schedules(response_bytes),
            self._extract_associated_tutorial_information(response_bytes),
            self._extract_associated_course_information(response_bytes),
            self._extract_responsible_persons_from_course_page(response_bytes),
            self._extract_associated_institutions_from_course_page(response_bytes),
        )

    def _does_course_type_have_too_many_results(self, course_type: int) -> bool:
        """Check if a course type returns too many results (>1000) requiring splitting."""
        error_message = "Ihre Anfrage lieferte mehr als 1000 Ergebnisse"
        response_bytes = self._make_safe_http_request(self._build_course_search_url("", course_type))
        tree = html.fromstring(response_bytes)
        p_tags = tree.xpath("//p")

        return any(error_message in p.text_content() for p in p_tags)

    def _make_safe_http_request(
        self,
        url: str,
        timeout: tuple[float, float] = (10, 30),
        retries: int = 5,
        max_backoff: float = 30,
    ) -> bytes:
        """Make HTTP request with retry logic and error handling.

        Args:
            url: The URL to fetch
            timeout: Tuple of (connect_timeout, read_timeout) in seconds
            retries: Maximum number of retry attempts
            max_backoff: Maximum sleep time between retries in seconds
        """
        for attempt in range(1, retries + 1):
            try:
                response = self.session.get(url, headers=self.get_random_header(), timeout=timeout)
                response.raise_for_status()
                return response.content
            except requests.exceptions.Timeout:
                sleep_time = min(2**attempt, max_backoff)
                self.logger.warning(
                    f"[Timeout {attempt}/{retries}] Request timed out (connect={timeout[0]}s, read={timeout[1]}s). "
                    f"Retrying in {sleep_time}s..."
                )
                if attempt < retries:
                    time.sleep(sleep_time)
            except requests.exceptions.RequestException as e:
                sleep_time = min(2**attempt, max_backoff)
                self.logger.warning(
                    f"[Retry {attempt}/{retries}] Request failed: {type(e).__name__}. " f"Retrying in {sleep_time}s..."
                )
                if attempt < retries:
                    time.sleep(sleep_time)
            except Exception as e:
                self.logger.error(f"[Error {attempt}/{retries}] Unexpected error fetching URL: {e}")
                if attempt < retries:
                    sleep_time = min(2**attempt, max_backoff)
                    time.sleep(sleep_time)

        self.logger.error(f"[FAIL] Giving up after {retries} retries")
        raise RuntimeError(f"Failed to fetch URL after {retries} retries")

    def _get_course_urls_with_search_filter(self, search_text: str, course_type: int) -> list[tuple[str, str]]:
        """Extract course URLs from search results for a given search filter."""
        request_bytes = self._make_safe_http_request(self._build_course_search_url(search_text, course_type))
        if self._is_invalid_semester(request_bytes):
            return []

        tree = html.fromstring(request_bytes)

        courses = tree.xpath('//a[@class="regular" and @title]')
        info = tree.xpath('//div[@class="InfoLeiste"]')

        expected_count = self._extract_result_count_from_info_bar(info)
        assert len(courses) == expected_count, "Mismatch in expected course count"

        return [
            (
                self._clean_and_normalize_string(c.text),
                self._clean_and_normalize_string(c.get("href")),
            )
            for c in courses
        ]

    def _is_invalid_semester(self, response_bytes: bytes) -> bool:
        return "Ungültiges Semester" in response_bytes.decode()

    def _extract_result_count_from_info_bar(self, info: Any) -> int:
        """Parse the course count from the info section of the HTML."""
        course_count = re.search(r"(\d+)\s+Treffer", info[0].text)
        assert course_count, f"Error parsing course count: {info}"
        return int(course_count.group(1))

    def _build_course_search_url(self, search_text: str, course_type: int) -> str:
        """Build URL for searching courses with specific filters."""
        semester_type = 1 if self.semester_type.value == "SOSE" else 2

        return (
            "https://lsf.verwaltung.uni-muenchen.de"
            + "/qisserver/rds?state=wsearchv"
            + "&search=1&subdir=veranstaltung&choice.veranstaltung.verartid=y&"
            + f"veranstaltung.verartid={course_type}"
            + f"&veranstaltung.dtxt={search_text}"
            + f"&veranstaltung.semester={self.year}{semester_type}"
            + "&P_start=0&P_anzahl=1000&P.sort=&_form=display"
        )

    def _get_all_available_course_type_ids(self) -> list[int]:
        """Get just the course type IDs without names."""
        return list(self._get_all_available_course_types_with_names().keys())

    def _get_all_available_course_types_with_names(self) -> dict[int, str]:
        """Retrieve all available coures types with their IDs and names."""
        course_types = {}
        url = self._build_course_types_discovery_url()
        request_bytes = self._make_safe_http_request(url)
        tree = html.fromstring(request_bytes)
        select = tree.get_element_by_id("veranstaltung.verartid")

        for option in select.xpath(".//option"):
            course_id = option.get("value")
            course_type = option.text_content().strip()
            if course_id:
                course_types[course_id] = course_type

        return course_types

    def _build_course_types_discovery_url(self) -> str:
        """Build the URL for discovering available course types."""
        return (
            "https://lsf.verwaltung.uni-muenchen.de/qisserver/"
            + "rds?state=change&type=5&moduleParameter="
            + "veranstaltungSearch&nextdir=change&next="
            + "search.vm&subdir=veranstaltung&_form=display&"
            + "function=search&clean=y&category=veranstaltung.search"
        )

    def _extract_navigation_tree_paths(self, response_bytes: bytes) -> Optional[list[list[str]]]:
        """Extract hierarchical navigation paths from the course page."""
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

    def _extract_course_base_information(self, response_bytes: bytes) -> CourseBaseInfo:
        """Extract basic course information including persons and institutions."""
        base_info_dict: dict[str, Any] = {
            "institutions": self._extract_associated_institutions_from_course_page(response_bytes),
        }
        return CourseBaseInfo(**(base_info_dict | self._extract_basic_course_data_from_html(response_bytes)))

    def _extract_responsible_persons_from_course_page(self, html_text: Any) -> Optional[list[Person]]:
        """Extract responsible persons/lecturers from the course page."""
        tree = html.fromstring(html_text)
        persons_table = tree.xpath('//table[@summary="Verantwortliche Dozenten"]')
        if len(persons_table) == 0:
            return None

        persons = []
        for table in persons_table:
            for row in table.xpath(".//tr"):
                if len(row_entrys := row.xpath(".//td")) == 0:
                    continue
                person_raw = row_entrys[0].text_content().strip()

                if person_raw == "keine öffentliche Person":
                    continue
                persons.append(Person.from_str(self._clean_and_normalize_string(person_raw)))

        return persons if len(persons) > 0 else None

    def _extract_associated_institutions_from_course_page(
        self,
        html_content: Any,
    ) -> Optional[list[Institution]]:
        """Extract associated institutions from the course page."""
        tree = html.fromstring(html_content)
        rows = tree.xpath("//table[@summary='Übersicht über die zugehörigen Einrichtungen']//tr")

        institutions = []
        for row in rows:
            link = row.xpath(".//a[@class='regular']")
            if link:
                name = self._clean_and_normalize_string(link[0].text_content())
                institutions.append(Institution(name=name))

        return institutions

    def _extract_basic_course_data_from_html(self, html_text: Any) -> dict[str, Optional[Any]]:
        """Extract basic data from the course's 'Grunddaten' table."""
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

    def _extract_associated_course_information(self, response_bytes: bytes) -> Optional[list[AssociatedClass]]:
        """Extract information about associated courses."""
        course_data = self._extract_data_from_table_with_summary(response_bytes, "Zugehörige Veranstaltungen")

        if not course_data:
            return None

        for course_info in course_data:
            number = course_info["Nr."]
            hours = course_info["SWS"]
            course_info["number"] = number if number else None
            course_info["weekly_hours"] = float(hours) if hours else None

        return [AssociatedClass(**table) for table in course_data]

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

    def _extract_additional_course_information(self, response_bytes: bytes) -> Optional[AdditionInformation]:
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

                additional_data[key] = html_to_markdown(inner_html)

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
        """Extract information about exams associated with the course."""
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

    def _extract_course_material_information(self, response_bytes: bytes) -> Optional[list[CourseMaterial]]:
        """Extract information about course materials and their validity periods."""
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
                CourseMaterial(
                    valid_from=(dt.strptime(row["gültig von"], "%d.%m.%Y").date() if row["gültig von"] else None),
                    valid_to=(dt.strptime(row["gültig bis"], "%d.%m.%Y").date() if row["gültig bis"] else None),
                    file_name=row["Dateiname"],
                    description=row["Beschreibung"],
                )
                for row in table_rows
            ]

        return material

    def _extract_associated_study_programs(self, response_bytes: bytes) -> Optional[list[AssociatedProgram]]:
        """Extract information about study programs associated with the course."""
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

    def _extract_course_session_schedules(self, response_bytes: bytes) -> Optional[list[CourseSession]]:
        """Extract course session schedules from the response bytes."""
        tree = html.fromstring(response_bytes)
        session_table = tree.xpath("//table[@summary='Übersicht über alle Veranstaltungstermine']")

        if len(session_table) == 0:
            return None

        sessions = []
        for table in session_table:
            column_headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            table_caption = c[0] if (c := table.xpath(".//caption/text()")) else None

            for table_row in table.xpath(".//tr[position()>1]"):
                cells = table_row.xpath("td")
                row_data = {
                    header: self._clean_and_normalize_string(cell.text_content())
                    for header, cell in zip(column_headers, cells)
                }

                # Extract room_id and building_id from the floor plan link in the Raum column
                raum_index = column_headers.index("Raum") if "Raum" in column_headers else None
                room_id = None
                building_id = None
                if raum_index is not None and raum_index < len(cells):
                    room_id, building_id = self._extract_room_and_building_from_cell(cells[raum_index])

                sessions.append(
                    CourseSession(
                        caption=table_caption,
                        weekday=self._parse_weekday(row_data["Tag"]),
                        starting_time=self._extract_start_time(row_data["Zeit"]),
                        ending_time=self._extract_end_time(row_data["Zeit"]),
                        timing_type=self._extract_time_type(row_data["Zeit"]),
                        rhythm=row_data["Rhythmus"] or None,
                        duration_start=self._parse_duration_start(row_data["Dauer"]),
                        duration_end=self._parse_duration_end(row_data["Dauer"]),
                        room_id=room_id,
                        building_id=building_id,
                        lecturer=row_data["Lehrperson"] or None,
                        remark=row_data["Bemerkung"] or None,
                        cancelled_dates=row_data["fällt aus am"] or None,
                    )
                )

        return sessions

    def _extract_room_and_building_from_cell(self, cell_element) -> tuple[Optional[str], Optional[str]]:
        """Extract room ID and building ID from the floor plan (Geschossplan) link.

        The floor plan URL format is:
        http://www.uni-muenchen.de/raumfinder/index.html#/part/bt1507/map?room=150701108_

        Returns a tuple of (room_id, building_id):
        - room_id: e.g., '150701108_'
        - building_id: e.g., 'bt1507'
        """
        # Look for raumfinder link containing the room parameter
        room_links = cell_element.xpath(".//a[contains(@href, 'raumfinder')]/@href")

        if not room_links:
            return None, None

        href = room_links[0]

        # Extract room parameter from URL (format: ...?room=150701108_)
        room_id = None
        room_match = re.search(r"[?&]room=([^&]+)", href)
        if room_match:
            room_id = room_match.group(1)

        # Extract building_id from URL (format: .../part/bt1507/map...)
        building_id = None
        building_match = re.search(r"/part/(bt\d+)/", href)
        if building_match:
            building_id = building_match.group(1)

        return room_id, building_id

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
    def _extract_time_type(time: str) -> Optional[CourseStartTypeEnum]:
        """Extract the type of course start from a time string."""
        if "s.t." in time:
            return CourseStartTypeEnum.SINE_TEMPORE
        if "c.t." in time:
            return CourseStartTypeEnum.CUM_TEMPORE
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
        """Parse the course information URL from the course page."""
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


class LSFSequentialCrawler(LSFCrawler):
    def __init__(self, year: int, semester_type: SemesterTypeEnum):
        super().__init__()
        self.set_crawling_parameters(year, semester_type)
        self._course_urls: list[tuple[str, str]] = []

    def __iter__(self) -> Iterator[Course]:
        if self._course_urls == []:
            self._course_urls = self._crawl_all_course_urls_sequentially()

        for title, url in self._course_urls:
            yield self.build_complete_course_object(title, url)

    def __len__(self):
        return len(self._course_urls)


class LSFParallelCrawler(LSFCrawler):
    def __init__(self, year: int, semester_type: SemesterTypeEnum):
        super().__init__()
        self.set_crawling_parameters(year, semester_type)
        self._course_urls: list[tuple[str, str]] = []

    def __iter__(self) -> Iterator[Course]:
        if self._course_urls == []:
            self._course_urls = self._crawl_course_urls_in_parallel()
            self.logger.info(f"Starting parallel crawl of {len(self._course_urls)} courses with {self.workers} workers")

        completed_count = 0
        failed_count = 0

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_url = {
                executor.submit(self.build_complete_course_object, title, url): (
                    title,
                    url,
                )
                for title, url in self._course_urls
            }

            for future in as_completed(future_to_url):
                try:
                    course = future.result()
                    completed_count += 1
                    yield course
                except Exception as e:
                    failed_count += 1
                    title, url = future_to_url[future]
                    self.logger.error(
                        f"Course '{title}' failed (completed: {completed_count}, failed: {failed_count}): {e}"
                    )

        self.logger.info(f"Parallel crawl finished. Completed: {completed_count}, Failed: {failed_count}")

    def __len__(self):
        return len(self._course_urls)


def main() -> None:
    crawler = LSFCrawler()
    print([l.to_dict() for l in crawler.crawl_all_courses_parallel(2025, SemesterTypeEnum.SUMMER_SEMESTER)])


if __name__ == "__main__":
    main()
