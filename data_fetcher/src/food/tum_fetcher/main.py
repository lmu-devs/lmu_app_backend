from typing import Dict, Optional

import menu_parser
from entities import Canteen, Week


def get_menu_parsing_strategy(canteen: Canteen) -> Optional[menu_parser.MenuParser]:
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

    # print(enum_json_creator.enum_to_api_representation_dict(list(Canteen)))

    canteen = Canteen.get_canteen_by_str("STUBISTRO_OETTINGSTR")
    
    # get required parser
    parser = get_menu_parsing_strategy(canteen)
    if not parser:
        print("Canteen parser not found")
        return

    # parse menu
    menus = parser.parse(canteen)

    # print menu
    if menus is None:
        print("Error. Could not retrieve menu(s)")

    weeks = Week.to_weeks(menus)
    for calendar_week in weeks:
        print(weeks[calendar_week])


if __name__ == "__main__":
    main()