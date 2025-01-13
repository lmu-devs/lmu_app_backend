from typing import Dict, Optional

import menu_parser
from entities import Week

from shared.src.enums import CanteenEnum


def get_menu_parsing_strategy(canteen: CanteenEnum) -> Optional[menu_parser.MenuParser]:
    parsers = {
        menu_parser.StudentenwerkMenuParser,
        # menu_parser.FMIBistroMenuParser,
        # menu_parser.IPPBistroMenuParser,
        # menu_parser.MedizinerMensaMenuParser,
        # menu_parser.StraubingMensaMenuParser,
        # menu_parser.MensaBildungscampusHeilbronnParser,
    }
    # set parsing strategy based on canteen
    for parser in parsers:
        if canteen in parser.canteens:
            return parser()
    return None


def main():

    canteen = CanteenEnum.STUBISTRO_OETTINGENSTR
    
    # get required parser
    parser = get_menu_parsing_strategy(canteen)
    if not parser:
        print("Canteen parser not found")
        return

    # parse menu
    menus = parser.parse(canteen)

    if menus is None:
        print("Error. Could not retrieve menu(s)")

    # weeks = Week.to_weeks(menus)
    # for calendar_week in weeks:
    #     print(weeks[calendar_week])
    
    print(menus)


if __name__ == "__main__":
    main()