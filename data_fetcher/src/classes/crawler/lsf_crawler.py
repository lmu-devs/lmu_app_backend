import codecs
from collections import defaultdict
import threading
from typing import Any, Optional
import concurrent.futures
import tqdm
import requests
import re
import time
from datetime import time as Time, date as Date, datetime as dt
from urllib.parse import urlparse, parse_qs, unquote
from lxml import html
import random

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
    def __init__(self) -> None:
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.workers = 16
        self.year: Optional[int] = None
        self.semster_type: Optional[SemesterTypeEnum] = None

    def crawl_all_lectures(
        self, year: int, semester_type: SemesterTypeEnum
    ) -> list[Lecture]:
        self.year = year
        self.semester_type = semester_type
        lecture_urls = self.crawl_lecture_urls()
        return self.crawl_lectures(lecture_urls)

    def crawl_lecture_urls(self) -> list[tuple[str, str]]:
        lecture_urls = []
        class_type_ids = self.crawl_class_types().keys()
        for type_id in tqdm.tqdm(class_type_ids, desc="Getting lecture urls"):
            lecture_urls += self.crawl_lectures_of_type(type_id)
        return lecture_urls

    def crawl_lectures(self, urls: list[tuple[str, str]]) -> list[Lecture]:
        lectures = []
        for url in tqdm.tqdm(urls, desc="Crawling lecture informations"):
            tqdm.tqdm.write(f"Processing lecture: {url}")
            lectures += [self.build_lecture(url)]
        return lectures

    def crawl_lectures_of_type(self, type_id: int) -> list[tuple[str, str]]:
        if self._is_class_type_to_big(type_id):
            return self._split_crawl_with_alpabet(type_id)
        else:
            return self._crawl_lectures("", type_id)

    def build_lecture(self, name_url: tuple[str, str]) -> Lecture:
        name, url = name_url
        response_bytes = self.safe_request(url)
        return Lecture.from_tuple(
            (name, url, self._crawl_tree_path(response_bytes)),
            self.crawl_class_base_info(response_bytes),
            self.crawl_additional_information(response_bytes),
            self.crawl_enrollment_deadlines(response_bytes),
            self.crawl_associated_programs(response_bytes),
            self.crawl_class_material(response_bytes),
            self.crawl_associated_exams(response_bytes),
            self.crawl_exam_information(response_bytes),
            self.crawl_class_session(response_bytes),
            self.crawl_associated_tutorials(response_bytes),
            self.crawl_associated_classes(response_bytes),
        )

    def crawl_all_lectures_parallel(
        self, year: int, semester_type: SemesterTypeEnum
    ) -> list[Lecture]:
        self.year = year
        self.semester_type = semester_type
        lecture_urls = self.crawl_lecture_urls_parallel()
        return self.crawl_lectures_parallel(lecture_urls)

    def crawl_lecture_urls_parallel(self) -> list[tuple[str, str]]:
        class_types = self.crawl_class_types()
        all_lecture_tuples: list[tuple[str, str]] = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            futures = {
                executor.submit(self.crawl_lectures_of_type, type_id): type_id
                for type_id in class_types.keys()
            }
            for future in tqdm.tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Collecting lectures",
            ):
                all_lecture_tuples.extend(future.result())
        return all_lecture_tuples

    def crawl_lectures_parallel(
        self, lecture_urls: list[tuple[str, str]]
    ) -> list[Lecture]:
        lectures = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            futures = {
                executor.submit(self.build_lecture, name_url): name_url
                for name_url in lecture_urls
            }
            for future in tqdm.tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Collecting and parsing lecture information",
            ):
                try:
                    lectures.append(future.result())
                except Exception as e:
                    raise Exception(f"❌ Error while building lecture: {e}")

        return lectures

    def _split_crawl_with_alpabet(self, type_id: int) -> list[tuple[str, str]]:
        lectures: list[tuple[str, str]] = []
        german_chars = list("abcdefghijklmnopqrstuvwxyzäöüß")
        for ch in german_chars:
            lectures += self._crawl_lectures(ch, type_id)
        return lectures

    def _is_class_type_to_big(self, class_type: int) -> bool:
        error_message = "Ihre Anfrage lieferte mehr als 1000 Ergebnisse"
        response_bytes = self.safe_request(self._get_classes_url("", class_type))
        tree = html.fromstring(response_bytes)
        p_tags = tree.xpath("//p")
        return any(error_message in p.text_content() for p in p_tags)

    def safe_request(self, url: str, timeout: float = 10, retries: int = 10) -> bytes:
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                return response.content
            except Exception as e:
                tqdm.tqdm.write(
                    f"[Retry {attempt}/{retries}] Error fetching {url}: {e}"
                )
                if attempt < retries:
                    time.sleep(attempt)
                else:
                    tqdm.tqdm.write(f"[FAIL] Giving up on {url}")
        raise RuntimeError(f"Failed to fetch {url} after {retries} retries")

    def _crawl_lectures(
        self, search_text: str, class_type: int
    ) -> list[tuple[str, str]]:
        request_bytes = self.safe_request(
            self._get_classes_url(search_text, class_type)
        )
        tree = html.fromstring(request_bytes)
        classes = tree.xpath('//a[@class="regular" and @title]')
        info = tree.xpath('//div[@class="InfoLeiste"]')
        assert len(classes) == self._parse_class_count(info)
        return [
            (self.clean_string(c.text), self.clean_string(c.get("href")))
            for c in classes
        ]

    def _parse_class_count(self, info: Any) -> int:
        class_count = re.search(r"(\d+)\s+Treffer", info[0].text)
        assert class_count, f"Error parsing class count: {info}"
        return int(class_count.group(1))

    def _get_classes_url(self, search_text: str, class_type: int) -> str:
        semeseter_type = 1 if self.semester_type.value == "SOSE" else 2
        return (
            "https://lsf.verwaltung.uni-muenchen.de"
            + "/qisserver/rds?state=wsearchv"
            + "&search=1&subdir=veranstaltung&choice.veranstaltung.verartid=y&"
            + f"veranstaltung.verartid={class_type}"
            + f"&veranstaltung.dtxt={search_text}"
            + f"&veranstaltung.semester={self.year}{semeseter_type}"
            + "&P_start=0&P_anzahl=1000&P.sort=&_form=display"
        )

    def crawl_class_types(self) -> dict[int, str]:
        class_types = {}
        url = (
            "https://lsf.verwaltung.uni-muenchen.de/qisserver/"
            + "rds?state=change&type=5&moduleParameter="
            + "veranstaltungSearch&nextdir=change&next="
            + "search.vm&subdir=veranstaltung&_form=display&"
            + "function=search&clean=y&category=veranstaltung.search"
        )
        request_bytes = self.safe_request(url)
        tree = html.fromstring(request_bytes)
        select = tree.get_element_by_id("veranstaltung.verartid")
        for option in select.xpath(".//option"):
            class_id = option.get("value")
            class_type = option.text_content().strip()
            if class_id:
                class_types[class_id] = class_type
        return class_types

    def _crawl_tree_path(self, response_bytes: bytes) -> Optional[list[list[str]]]:
        tree = html.fromstring(response_bytes)
        nodes = tree.xpath("//div[contains(@style, 'padding-left')]/a")
        paths = []
        indent_stack = []

        for node in nodes:
            parent_div = node.getparent()
            style = parent_div.attrib.get("style", "")
            text = self.clean_string(node.text_content().strip())

            try:
                indent = int(style.split("padding-left:")[1].split("px")[0].strip())
            except Exception:
                continue

            while indent_stack and indent_stack[-1][0] >= indent:
                indent_stack.pop()

            indent_stack.append((indent, text))

            if parent_div.xpath(".//span[@class='warnung']"):
                current_path = [text for _, text in indent_stack]
                paths.append(current_path)
        return paths if paths else None

    def crawl_associated_tutorials(
        self, response_bytes: bytes
    ) -> Optional[list[AssociatedTutorial]]:
        tables = self.crawl_table_content_from_summary(
            response_bytes, "Zugehörige Übungen"
        )
        if not tables:
            return None
        for table in tables:
            number = table["Nr."]
            hours = table["SWS"]
            table["number"] = number if number else None
            table["weekly_hours"] = float(hours) if hours else None
        return [AssociatedTutorial(**table) for table in tables]

    def crawl_associated_classes(
        self, response_bytes: bytes
    ) -> Optional[list[AssociatedClass]]:
        tables = self.crawl_table_content_from_summary(
            response_bytes, "Zugehörige Veranstaltungen"
        )
        if not tables:
            return None
        for table in tables:
            number = table["Nr."]
            hours = table["SWS"]
            table["number"] = number if number else None
            table["weekly_hours"] = float(hours) if hours else None
        return [AssociatedClass(**table) for table in tables]

    def crawl_enrollment_deadlines(
        self, response_bytes: bytes
    ) -> Optional[EnrollmentDeadline]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary='Übersicht über die zugehörigen Belegfristen'"
            + "and not(ancestor::table)]"
        )

        if len(tables) != 1:
            return None

        rows = tables[0].xpath("./tr")
        program_rows = []
        other_rows = []
        current_section = None

        for row in rows:
            if row.xpath("./td[@colspan]"):
                text = row.text_content().strip().lower()
                if "studiengangsbezogene fristen" in text:
                    current_section = "program"
                elif "sonstige fristen" in text:
                    current_section = "other"
                else:
                    current_section = None
                continue
            row_html = self.clean_string(str(html.tostring(row, encoding="unicode")))
            if current_section == "program":
                program_rows.append(row_html)
            elif current_section == "other":
                other_rows.append(row_html)

        def wrap_table(rows: list[str]) -> Optional[str]:
            lines = "\n".join(rows)
            return f"<table>{lines}</table>" if rows else None

        return EnrollmentDeadline(
            program_associated_deadline=wrap_table(program_rows),
            other_deadlines=wrap_table(other_rows),
        )

    def crawl_exam_information(
        self, response_bytes: bytes
    ) -> Optional[list[ExamInformation]]:
        tables = self.crawl_table_content_from_summary(
            response_bytes, "Übersicht über die zugehörigen PORG"
        )
        if not tables:
            return None
        for table in tables:
            registration_duration = table["Anmeldungszeitraum"]
            table["registration_start"] = (
                self.parse_duration_start(registration_duration)
                if registration_duration
                else None
            )
            table["registration_end"] = (
                self.parse_duration_end(registration_duration)
                if registration_duration
                else None
            )
            table["ECTS"] = (
                self.parse_ects_from_text(table["ECTS"]) if table["ECTS"] else None
            )
            table["Datum"] = (
                dt.strptime(table["Datum"], "%d.%m.%Y") if table["Datum"] else None
            )
        return [ExamInformation(**data) for data in tables]

    def crawl_additional_information(
        self, response_bytes: bytes
    ) -> Optional[AdditionInformation]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary='Weitere Angaben zur Veranstaltung'"
            + "and not(ancestor::table)]"
        )
        data: defaultdict = defaultdict(lambda: None)

        if not tables:
            return None
        assert len(tables) == 1
        table = tables[0]

        for tr in table.xpath(".//tr"):
            th = tr.xpath("./th")
            td = tr.xpath("./td")
            if th and td:
                key = str(th[0].text_content().strip())
                if len(td[0]):
                    inner_html = "".join(
                        self.clean_string(str(html.tostring(child, encoding="unicode")))
                        for child in td[0]
                    )
                else:
                    inner_html = self.clean_string(str(td[0].text_content().strip()))
                data[key] = inner_html
        return AdditionInformation(**data)

    def crawl_table_content_from_summary(
        self, response_bytes: bytes, summary: str
    ) -> Optional[list[dict]]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(f"//table[@summary='{summary}']")
        content = []
        if len(tables) == 0:
            return None

        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            for tr in table.xpath(".//tr[position()>1]"):
                cells = [
                    (
                        data
                        if (
                            (data := self.clean_string(td.text_content())) != ""
                            and data != "-"
                        )
                        else None
                    )
                    for td in tr.xpath("td")
                ]
                content.append(dict(zip(headers, cells)))
        return content

    def crawl_associated_exams(
        self, response_bytes: bytes
    ) -> Optional[list[AssociatedExam]]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary=" + "'Übersicht über die zugehörigen Prüfungen']"
        )
        exams = []
        if len(tables) == 0:
            return None

        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            rows = []
            for tr in table.xpath(".//tr[position()>1]"):
                cells = [
                    (
                        data
                        if ((data := self.clean_string(td.text_content())) != "")
                        else None
                    )
                    for td in tr.xpath("td")
                ]
                row_data = dict(zip(headers, cells))
                rows.append(row_data)
            exams += [
                AssociatedExam(
                    module_name=self.remove_ects_from_text(row["Modul"]),
                    program_name=row["Stg"],
                    ects=self.parse_ects_from_text(
                        row["ECTS"] or "" + row["Modul"] or ""
                    ),
                    module_classification=row["KzFa"],
                    degree=row["Abschl"],
                    module_id=row["Modulnr"],
                    exam_id=row["Pnr"],
                    po_version=row["Version"],
                )
                for row in rows
            ]
        return exams

    @staticmethod
    def remove_ects_from_text(text: str) -> str:
        return re.sub(r"\s*\(?\d+\s*ECTS\)?", "", text).strip()

    @staticmethod
    def parse_int(raw_int: str) -> Optional[int]:
        try:
            return int(raw_int)
        except Exception:
            return None

    @staticmethod
    def parse_float(raw_float: str) -> Optional[float]:
        try:
            return float(raw_float)
        except Exception:
            return None

    @staticmethod
    def parse_ects_from_text(text: str) -> Optional[int]:
        match = re.search(r"(\d+)\s*ECTS", text)
        if match:
            return int(match.group(1))
        return None

    def crawl_class_material(
        self, response_bytes: bytes
    ) -> Optional[list[ClassMaterial]]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary="
            + "'Übersicht über die zugehörigen Medien oder so ähnlich']"
        )
        material = []
        if len(tables) == 0:
            return None

        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            rows = []
            for tr in table.xpath(".//tr[position()>1]"):
                cells = [
                    (
                        data
                        if ((data := self.clean_string(td.text_content())) != "")
                        else None
                    )
                    for td in tr.xpath("td")
                ]
                row_data = dict(zip(headers, cells))
                rows.append(row_data)

            material += [
                ClassMaterial(
                    valid_from=(
                        dt.strptime(row["gültig von"], "%d.%m.%Y").date()
                        if row["gültig von"]
                        else None
                    ),
                    valid_to=(
                        dt.strptime(row["gültig bis"], "%d.%m.%Y").date()
                        if row["gültig bis"]
                        else None
                    ),
                    file_name=row["Dateiname"],
                    description=row["Beschreibung"],
                )
                for row in rows
            ]
        return material

    def crawl_associated_programs(
        self, response_bytes: bytes
    ) -> Optional[list[AssociatedProgram]]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary='Übersicht über die zugehörigen Studiengänge']"
        )
        programs = []
        if len(tables) == 0:
            return None

        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            rows = []
            for tr in table.xpath(".//tr[position()>1]"):
                cells = [self.clean_string(td.text_content()) for td in tr.xpath("td")]
                row_data = dict(zip(headers, cells))
                rows.append(row_data)

            programs += [
                AssociatedProgram(
                    program_name=row["Studiengang"],
                    ects=self.parse_int(row["ECTS"].split(" ")[0]),
                    degree=row["Abschluss"],
                    module_classification=row["KzFa"],
                )
                for row in rows
            ]
        return programs

    def crawl_class_session(
        self, response_bytes: bytes
    ) -> Optional[list[ClassSession]]:
        tree = html.fromstring(response_bytes)
        tables = tree.xpath(
            "//table[@summary='Übersicht über alle Veranstaltungstermine']"
        )
        sessions = []
        if len(tables) == 0:
            return None

        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath(".//tr[1]/th")]
            caption = c[0] if (c := table.xpath(".//caption/text()")) else None
            rows = []
            for tr in table.xpath(".//tr[position()>1]"):
                cells = [self.clean_string(td.text_content()) for td in tr.xpath("td")]
                row_data = dict(zip(headers, cells))
                rows.append(row_data)

            sessions += [
                ClassSession(
                    caption=caption,
                    weekday=self.parse_weekday(row["Tag"]),
                    starting_time=self.parse_start_time(row["Zeit"]),
                    ending_time=self.parse_end_time(row["Zeit"]),
                    timing_type=self.parse_time_type(row["Zeit"]),
                    rythm=row["Rhythmus"] or None,
                    duration_start=self.parse_duration_start(row["Dauer"]),
                    duration_end=self.parse_duration_end(row["Dauer"]),
                    room=self.parse_room(row["Raum"]),
                    lecturer=row["Lehrperson"] or None,
                    remark=row["Bemerkung"] or None,
                    cancelled_dates=row["fällt aus am"] or None,
                )
                for row in rows
            ]
        return sessions

    @staticmethod
    def parse_room(room: str) -> Optional[str]:
        if room == "":
            return None
        return re.sub(r"\s+Geschossplan", "", room)

    @staticmethod
    def extract_times(time_str: str) -> list[str]:
        parts = time_str.split()
        time_regex = re.compile(r"\d{1,2}:\d{2}")
        times = [part for part in parts if time_regex.match(part)]
        return times

    @staticmethod
    def extract_dates(date_str):
        parts = date_str.split()
        date_regex = re.compile(r"\d{2}\.\d{2}\.\d{4}")
        dates = [part for part in parts if date_regex.match(part)]
        return dates

    def parse_duration_end(self, time: str) -> Optional[Date]:
        if len(dates := self.extract_dates(time)) < 2:
            return None
        end = dates[1]
        return dt.strptime(end, "%d.%m.%Y").date()

    def parse_duration_start(self, time: str) -> Optional[Date]:
        if len(dates := self.extract_dates(time)) < 1:
            return None
        start = dates[0]
        return dt.strptime(start, "%d.%m.%Y").date()

    @staticmethod
    def parse_time_type(time: str) -> Optional[LectureStartTypeEnum]:
        if "s.t." in time:
            return LectureStartTypeEnum.SINE_TEMPORE
        if "c.t." in time:
            return LectureStartTypeEnum.CUM_TEMPORE
        return None

    @staticmethod
    def convert_midnight(time: str) -> str:
        return "00:00" if time == "24:00" else time

    def parse_end_time(self, time: str) -> Optional[Time]:
        if len(time_points := self.extract_times(time)) < 2:
            return None
        end_time = self.convert_midnight(time_points[1])
        return dt.strptime(end_time, "%H:%M").time()

    def parse_start_time(self, time: str) -> Optional[Time]:
        if len(time_points := self.extract_times(time)) < 1:
            return None
        start_time = self.convert_midnight(time_points[0])
        return dt.strptime(start_time, "%H:%M").time()

    @staticmethod
    def parse_weekday(day: str) -> Optional[WeekdayEnum]:
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

    def crawl_class_base_info(self, response_bytes: bytes) -> ClassBaseInfo:
        base_info_dict: dict[str, Any] = {
            "persons": self.get_persons_from_lecture_html(response_bytes),
            "institutions": self.get_institutions_from_lecture_html(response_bytes),
        }
        return ClassBaseInfo(
            **(base_info_dict | self.get_basic_info_from_html(response_bytes))
        )

    def get_institutions_from_lecture_html(
        self,
        html_content: Any,
    ) -> Optional[list[Institution]]:
        tree = html.fromstring(html_content)
        rows = tree.xpath(
            "//table[@summary='Übersicht über die zugehörigen Einrichtungen']//tr"
        )

        institutions = []
        for row in rows:
            link = row.xpath(".//a[@class='regular']")
            if link:
                name = self.clean_string(link[0].text_content())
                institutions.append(Institution(name=name))
        return institutions

    def get_basic_info_from_html(self, html_text: Any) -> dict[str, Optional[Any]]:
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
                value = self.clean_string(data.text_content())

                if key == "Weitere Links":
                    base_info_dict[key] = self.parse_link(data)
                    continue
                if key == "SWS":
                    base_info_dict[key] = self.parse_float(value)
                    continue
                if key == "Max. Teilnehmer/-innen":
                    base_info_dict[key] = self.parse_int(value)
                base_info_dict[key] = None if value == "" else value
        return base_info_dict

    def parse_link(self, data) -> Optional[str]:
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
    def clean_string(raw: str) -> str:
        unescaped = (
            codecs.decode(raw, "unicode_escape").encode("latin1").decode("utf-8")
        )
        return re.sub(r"\s+", " ", unescaped).strip()

    def get_persons_from_lecture_html(self, html_text: Any) -> Optional[list[Person]]:
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
            persons.append(Person.from_str(self.clean_string(person_raw)))

        return persons if len(persons) > 0 else None


def main() -> None:
    crawler = LSFCrawler()
    print(
        [
            l.to_dict()
            for l in crawler.crawl_all_lectures_parallel(
                2025, SemesterTypeEnum.SUMMER_SEMESTER
            )
        ]
    )


if __name__ == "__main__":
    main()
