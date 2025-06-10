import tqdm
import requests
import re
from lxml import html

from shared.src.enums.classes_enum import SemesterTypeEnum
from ..models.lecture import Lecture


class LSFCrawler:
    def __init__(self) -> None:
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.year: int = None
        self.semster_type: SemesterTypeEnum = None

    def crawl_all_lectures(
        self, year: int, semester_type: SemesterTypeEnum
    ) -> list[Lecture]:
        self.year = year
        self.semester_type = semester_type
        lectures = []
        class_types = self.crawl_class_types()

        for type_id in tqdm.tqdm(class_types.keys(), desc="Collecting lectures"):
            if self._is_class_type_to_big(type_id):
                lectures += self._split_crawl_with_alpabet(type_id)
            else:
                lectures += self._crawl_lectures("", type_id)

        return [
            Lecture.from_tuple((name, url, self._crawl_tree_path(url)))
            for name, url in tqdm.tqdm(lectures, desc="Collecting tree paths")
        ]

    def _split_crawl_with_alpabet(self, type_id: int) -> list[tuple[str, str]]:
        lectures = []
        german_chars = list("abcdefghijklmnopqrstuvwxyzäöüß")
        for ch in german_chars:
            lectures += self._crawl_lectures(ch, type_id)
        return lectures

    def _is_class_type_to_big(self, class_type: int) -> bool:
        error_message = "Ihre Anfrage lieferte mehr als 1000 Ergebnisse"
        response = requests.get(
            self._get_classes_url("", class_type),
            headers=self.headers,
        )
        tree = html.fromstring(response.content)
        p_tags = tree.xpath("//p")
        return any(error_message in p.text_content() for p in p_tags)

    def _crawl_lectures(
        self, search_text: str, class_type: int
    ) -> list[tuple[str, str]]:
        response = requests.get(
            self._get_classes_url(search_text, class_type),
            headers=self.headers,
        )
        tree = html.fromstring(response.content)
        classes = tree.xpath('//a[@class="regular" and @title]')
        info = tree.xpath('//div[@class="InfoLeiste"]')
        assert len(classes) == self._parse_class_count(info)
        return [[c.text, c.get("href")] for c in classes]

    def _parse_class_count(self, info: str) -> int:
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
        response = requests.get(url, headers=self.headers)
        tree = html.fromstring(response.content)
        select = tree.get_element_by_id("veranstaltung.verartid")
        for option in select.xpath(".//option"):
            class_id = option.get("value")
            class_type = option.text_content().strip()
            if class_id:
                class_types[class_id] = class_type
        return class_types

    def _crawl_tree_path(self, url: str) -> list[list[str]]:
        html_content = requests.get(url, headers=self.headers).content
        tree = html.fromstring(html_content)
        nodes = tree.xpath("//div[contains(@style, 'padding-left')]/a")
        paths = []
        indent_stack = []

        for node in nodes:
            parent_div = node.getparent()
            style = parent_div.attrib.get("style", "")
            text = node.text_content().strip()

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


def main() -> None:
    crawler = LSFCrawler()
    print(crawler.crawl_all_lectures(2025, SemesterTypeEnum.SUMMER_SEMESTER))


if __name__ == "__main__":
    main()
