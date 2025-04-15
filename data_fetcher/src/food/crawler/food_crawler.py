from typing import Dict, List, Optional

import data_fetcher.src.food.crawler.menu_parser as menu_parser
from data_fetcher.src.food.crawler.entities import Menu
from shared.src.enums import CanteenEnum


class FoodCrawler:
    def __init__(self):
        self.parsers = {
            menu_parser.StudentenwerkMenuParser,
            # menu_parser.FMIBistroMenuParser,
            # menu_parser.IPPBistroMenuParser,
            # menu_parser.MedizinerMensaMenuParser,
            # menu_parser.StraubingMensaMenuParser,
            # menu_parser.MensaBildungscampusHeilbronnParser,
        }

    def get_menu_parsing_strategy(self, canteen: CanteenEnum) -> Optional[menu_parser.MenuParser]:
        for parser in self.parsers:
            if canteen in parser.canteens:
                return parser()
        return None

    def get_menus(self, canteen: CanteenEnum) -> Optional[List[Menu]]:
        parser = self.get_menu_parsing_strategy(canteen)
        if not parser:
            print("Canteen parser not found")
            return None

        menus = parser.parse(canteen)
        if menus is None:
            print("Error. Could not retrieve menu(s)")
            return None

        return menus


def main():
    crawler = FoodCrawler()
    canteen = CanteenEnum.STUBISTRO_OETTINGENSTR

    menus = crawler.get_menus(canteen)

    for menu in menus:
        print(menu.menu_date)
        for dish in menu.dishes:
            print(dish.title)
            print(dish.prices)
            # print(dish.labels.text)
            existing_labels = [label.name for label in dish.labels]  # Changed to access label.text
            print(existing_labels)


if __name__ == "__main__":
    main()
