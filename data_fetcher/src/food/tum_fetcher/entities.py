from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class ApiRepresentable:
    def to_api_representation(self) -> Dict[str, object]:
        return {}


class Price:
    base_price: Optional[float]
    price_per_unit: Optional[float]
    unit: Optional[str]

    def __init__(
        self,
        base_price: Optional[float] = None,
        price_per_unit: Optional[float] = None,
        unit: Optional[str] = None,
    ):
        self.base_price = base_price
        self.price_per_unit = price_per_unit
        self.unit = unit

    def __repr__(self):
        if self.price_per_unit and self.unit:
            if isinstance(self.base_price, float):
                return f"{self.base_price: .2f}€ + {self.price_per_unit: .2f} {self.unit}"
            return f"{self.base_price} + {self.price_per_unit} {self.unit}"
        if isinstance(self.base_price, float):
            return f"{self.base_price: .2f}€"
        return f"{self.base_price}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self.base_price == other.base_price
                and self.price_per_unit == other.price_per_unit
                and self.unit == other.unit
            )
        return False

    def to_json_obj(self):
        return {"base_price": self.base_price, "price_per_unit": self.price_per_unit, "unit": self.unit}

    def __hash__(self) -> int:
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return (hash(self.base_price) << 1) ^ hash(self.price_per_unit) ^ hash(self.unit)


class Prices:
    students: Price | None
    staff: Price | None
    guests: Price | None

    def __init__(self, students: Price | None = None, staff: Price | None = None, guests: Price | None = None):
        self.students = students
        # fall back to the students price if there is only one price available
        if staff is None:
            self.staff = self.students
        else:
            self.staff = staff
        if guests is None:
            self.guests = self.students
        else:
            self.guests = guests

    def set_base_price(self, base_price: float) -> None:
        if self.students is not None:
            self.students.base_price = base_price
        if self.staff is not None:
            self.staff.base_price = base_price
        if self.guests is not None:
            self.guests.base_price = base_price

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.students == other.students and self.staff == other.staff and self.guests == other.guests
        return False

    def __repr__(self):
        return f"students: {self.students}, staff: {self.staff}, guests: {self.guests}"

    def to_json_obj(self):
        return {
            "students": self.students.to_json_obj() if self.students is not None else None,
            "staff": self.staff.to_json_obj() if self.staff is not None else None,
            "guests": self.guests.to_json_obj() if self.guests is not None else None,
        }

    def __hash__(self) -> int:
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return hash(self.students) ^ hash(self.staff) ^ hash(self.guests)


class Location:
    def __init__(self, address: str, latitude: float, longitude: float):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

    def to_json_obj(self):
        return {
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


class OpenHours:
    def __init__(
        self,
        mon: Optional[Tuple[str, str]] = None,
        tue: Optional[Tuple[str, str]] = None,
        wed: Optional[Tuple[str, str]] = None,
        thu: Optional[Tuple[str, str]] = None,
        fri: Optional[Tuple[str, str]] = None,
    ):
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri

    @staticmethod
    def day_to_obj(day: Optional[Tuple[str, str]]) -> Optional[Dict[str, str]]:
        if day:
            return {
                "start": day[0],
                "end": day[1],
            }
        return None

    def to_json_obj(self):
        return {
            "mon": self.day_to_obj(self.mon),
            "tue": self.day_to_obj(self.tue),
            "wed": self.day_to_obj(self.wed),
            "thu": self.day_to_obj(self.thu),
            "fri": self.day_to_obj(self.fri),
        }


class Canteen(ApiRepresentable, Enum):
    # Some of the canteens do not use the general Studentenwerk system and therefore do not have a url_id.
    def __init__(self, long_name: str, location: Location, url_id: int, queue_status: str, open_hours: OpenHours):
        self.long_name = long_name
        self.site = location
        self.url_id = url_id
        self.canteen_id = self.name.lower().replace("_", "-")
        self.queue_status = queue_status
        self.open_hours = open_hours
        
    STUBISTRO_OETTINGSTR = (
        "StuBistro Oettingenstraße",
        Location("Oettingenstraße 1, München", 48.148893, 11.579027),
        424,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )

    MENSA_ARCISSTR = (
        "Mensa Arcisstraße",
        Location("Arcisstraße 17, München", 48.14742, 11.56722),
        421,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    MENSA_GARCHING = (
        "Mensa Garching",
        Location("Boltzmannstraße 19, Garching", 48.268132, 11.672263),
        422,
        "https://mensa.liste.party/api/",
        OpenHours(("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:00")),
    )
    MENSA_LEOPOLDSTR = (
        "Mensa Leopoldstraße",
        Location("Leopoldstraße 13a, München", 48.156311, 11.582446),
        411,
        None,
        OpenHours(("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:00")),
    )
    MENSA_LOTHSTR = (
        "Mensa Lothstraße",
        Location("Lothstraße 13d, München", 48.153989, 11.552424),
        431,
        "https://api.betterhm.app/v1/capacity/MENSA_LOTHSTR",
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    MENSA_MARTINSRIED = (
        "Mensa Martinsried",
        Location("Großhaderner Straße 44, Plategg", 48.109824, 11.460006),
        412,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    MENSA_PASING = (
        "Mensa Pasing",
        Location("Am Stadtpark 20, München", 48.141568, 11.451119),
        432,
        "https://api.betterhm.app/v1/capacity/MENSA_PASING",
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    MENSA_WEIHENSTEPHAN = (
        "Mensa Weihenstephan",
        Location(
            "Maximus-von-Imhof-Forum 5, Freising",
            48.39959,
            11.723147,
        ),
        423,
        None,
        OpenHours(("11:00", "13:30"), ("11:00", "13:30"), ("11:00", "13:30"), ("11:00", "13:30"), ("11:00", "13:30")),
    )
    STUBISTRO_ARCISSTR = (
        "StuBistro Arcisstraße",
        Location("Arcisstraße 12, 80333 München", 48.156486, 11.581872),
        450,
        None,
        OpenHours(("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00")),
    )
    STUBISTRO_GOETHESTR = (
        "StuBistro Goethestraße",
        Location("Goethestraße 70, München", 48.131396, 11.558264),
        418,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    STUBISTRO_BUTENANDSTR = (
        "StuBistro Butenandstraße",
        Location(
            "Butenandtstraße 13, Gebäude F, München",
            48.11363,
            11.46503,
        ),
        414,
        None,
        OpenHours(("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "14:30")),
    )
    STUBISTRO_ROSENHEIM = (
        "StuBistro Rosenheim",
        Location("Hochschulstraße 1, Rosenheim", 47.867344, 12.107559),
        441,
        None,
        OpenHours(("09:00", "15:30"), ("09:00", "15:30"), ("09:00", "15:30"), ("09:00", "15:30"), ("09:00", "14:00")),
    )
    STUBISTRO_SCHELLINGSTR = (
        "StuBistro Schellingstraße",
        Location(
            "Schellingstraße 3, München",
            48.148893,
            11.579027,
        ),
        416,
        None,
        OpenHours(("09:00", "16:30"), ("09:00", "16:30"), ("09:00", "16:30"), ("09:00", "16:30"), ("09:00", "14:30")),
    )
    STUBISTRO_MARTINSRIED = (
        "StuBistro Martinsried",
        Location("Großhadernerstr. 9a, 82152 Planegg-Martinsried", 48.1105075, 11.4574515),
        415,
        None,
        OpenHours(("08:30", "14:30"), ("08:30", "14:30"), ("08:30", "14:30"), ("08:30", "14:30"), ("08:30", "14:30")),
    )
    STUCAFE_ADALBERTSTR = (
        "StuCafé Adalbertstraße",
        Location("Adalbertstraße 5, München", 48.151507, 11.581033),
        512,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    STUCAFE_AKADEMIE_WEIHENSTEPHAN = (
        "StuCafé Akademie Weihenstephan",
        Location(
            "Alte Akademie 1, Freising",
            48.3948,
            11.729338,
        ),
        526,
        None,
        OpenHours(("08:00", "14:30"), ("08:00", "14:30"), ("08:00", "14:30"), ("08:00", "14:30"), ("08:00", "14:00")),
    )
    STUCAFE_WEIHENSTEPHAN_MAXIMUS = (
        "StuCafé Weihenstephan-Maximus",
        Location(
            "Maximus-von-Imhof-Forum 5, 85354 Freising",
            48.3995014,
            11.7210581,
        ),
        525,
        None,
        OpenHours(("08:30", "15:00"), ("08:30", "15:00"), ("08:30", "15:00"), ("08:30", "15:00"), ("08:30", "14:00")),
    )
    STUCAFE_BOLTZMANNSTR = (
        "StuCafé Boltzmannstraße",
        Location(
            "Boltzmannstraße 15, Garching",
            48.265768,
            11.667593,
        ),
        527,
        None,
        OpenHours(("08:00", "16:00"), ("08:00", "16:00"), ("08:00", "16:00"), ("08:00", "16:00"), ("08:00", "15:00")),
    )
    STUCAFE_CONNOLLYSTR = (
        "StuCafé Connollystraße",
        Location(
            "Connollystraße 32, München",
            48.179222,
            11.546377,
        ),
        425,
        None,
        OpenHours(("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "15:00"), ("09:00", "14:00")),
    )
    STUCAFE_GARCHING = (
        "StuBistro Garching",
        Location(
            "Boltzmannstraße 19, Garching",
            48.268268,
            11.6717,
        ),
        426,
        None,
        OpenHours(("09:00", "16:00"), ("09:00", "16:00"), ("09:00", "16:00"), ("09:00", "16:00"), ("09:00", "15:00")),
    )
    STUCAFE_KARLSTR = (
        "StuCafé Karlstraße",
        Location("Karlstraße 6, München", 48.142759, 11.568432),
        532,
        None,
        OpenHours(("08:15", "15:00"), ("08:15", "15:00"), ("08:15", "15:00"), ("08:15", "15:00"), ("08:15", "15:00")),
    )
    STUCAFE_PASING = (
        "StuCafé Pasing",
        Location("Am Stadtpark 20, München", 48.141568, 11.451119),
        534,
        "https://api.betterhm.app/v1/capacity/STUCAFE_PASING",
        OpenHours(("07:45", "16:15"), ("07:45", "16:15"), ("07:45", "16:00"), ("07:45", "16:00"), ("07:45", "14:30")),
    )
    IPP_BISTRO = (
        "IPP Bistro Garching",
        Location("Boltzmannstraße 2, 85748 Garching", 48.262371, 11.672702),
        None,
        None,
        OpenHours(("09:00", "17:00"), ("09:00", "17:00"), ("09:00", "17:00"), ("09:00", "17:00"), ("09:00", "15:00")),
    )
    FMI_BISTRO = (
        "FMI Bistro Garching",
        Location("Boltzmannstraße 3, 85748 Garching", 48.262408, 11.668028),
        None,
        None,
        OpenHours(("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00"), ("11:00", "14:00")),
    )
    MEDIZINER_MENSA = (
        "Mediziner Mensa",
        Location("Ismaninger Straße 22, 81675 München", 48.136569, 11.5993226),
        None,
        None,
        OpenHours(("08:00", "15:30"), ("08:00", "15:30"), ("08:00", "15:30"), ("08:00", "15:30"), ("08:00", "15:30")),
    )
    MENSA_STRAUBING = (
        "Mensa Straubing",
        Location("Schulgasse 22, 94315 Straubing", 48.8845587, 12.5829364),
        None,
        None,
        OpenHours(("07:30", "15:00"), ("07:30", "15:00"), ("07:30", "15:00"), ("07:30", "15:00"), ("07:30", "14:30")),
    )
    MENSA_BILDUNGSCAMPUS_HEILBRONN = (
        "Mensa Buildungscampus Heilbronn",
        Location("Bildungscampus 8, 74076 Heilbronn", 49.14863559683538, 9.21598792582061),
        None,
        None,
        OpenHours(("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30"), ("11:00", "14:30")),
    )

    @staticmethod
    def get_canteen_by_str(canteen_str: str) -> Canteen:
        return Canteen[canteen_str.upper().replace("-", "_")]



class Label(ApiRepresentable, Enum):
    def __init__(self, text: str):
        self.text = text

    GLUTEN = "Gluten"
    WHEAT = "Weizen"
    RYE = "Roggen"
    BARLEY = "Gerste"
    OAT = "Hafer"
    SPELT = "Dinkel"
    HYBRIDS = "Hybridstämme"
    SHELLFISH = "Krebstiere"
    CHICKEN_EGGS = "Eier"
    FISH = "Fisch"
    PEANUTS = "Erdnüsse"
    SOY = "Soja"
    MILK = "Milch"
    LACTOSE = "Laktose"
    ALMONDS = "Mandeln"
    HAZELNUTS = "Haselnüsse"
    WALNUTS = "Walnüsse"
    CASHEWS = "Cashewnüsse"
    PECAN = "Pekanüsse"
    PISTACHIOES = "Pistazien"
    MACADAMIA = "Macadamianüsse"
    CELERY = "Sellerie"
    MUSTARD = "Senf"
    SESAME = "Sesam"
    SULPHURS = "Schwefeldioxid"
    SULFITES = "Sulfite"
    LUPIN = "Lupine"
    MOLLUSCS = "Weichtiere"
    SHELL_FRUITS = "Schalenfrüchte"

    BAVARIA = "Zertifizierte Qualität Bayern"
    MSC = "Marine Stewardship Council"
    DYESTUFF = "Farbstoffe"
    PRESERVATIVES = "Preservate"
    ANTIOXIDANTS = "Antioxidanten"
    FLAVOR_ENHANCER = "Geschmacksverstärker"
    WAXED = "Gewachst"
    PHOSPATES = "Phosphate"
    SWEETENERS = "Süßungsmittel"
    PHENYLALANINE = "Phenylaline"
    COCOA_CONTAINING_GREASE = "Kakaohaltiges Fett"
    GELATIN = "Gelatine"
    ALCOHOL = "Alkohol"
    PORK = "Schweinefleisch"
    BEEF = "Rinderfleisch"
    VEAL = "Kalbsfleisch"
    WILD_MEAT = "Wildfleisch"
    LAMB = "Lammfleisch"
    GARLIC = "Knoblauch"
    POULTRY = "Geflügel"
    CEREAL = "Getreide"
    MEAT = "Fleisch"
    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarisch"

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.name < other.name
        return NotImplemented

    @staticmethod
    def add_supertype_labels(labels: Set[Label]) -> None:
        # insert supertypes
        if labels & {
            Label.ALMONDS,
            Label.HAZELNUTS,
            Label.MACADAMIA,
            Label.CASHEWS,
            Label.PECAN,
            Label.PISTACHIOES,
            Label.SESAME,
            Label.WALNUTS,
        }:
            labels |= {Label.SHELL_FRUITS}
        if labels & {
            Label.BARLEY,
            Label.OAT,
            Label.RYE,
            Label.SPELT,
            Label.WHEAT,
        }:
            labels |= {Label.CEREAL}
        if labels & {Label.VEGAN}:
            labels |= {Label.VEGETARIAN}

        if labels & {
            Label.PORK,
            Label.BEEF,
            Label.VEAL,
        }:
            labels |= {Label.MEAT}

    def to_json_obj(self):
        return {
            "name": self.name,
            "text": self.text,
        }

    def to_api_representation(self) -> Dict[str, object]:
        return {
            "enum_name": self.name,
            "text": self.text,
        }


class Dish:
    name: str
    prices: Prices
    labels: Set[Label]
    dish_type: str

    def __init__(
        self,
        name: str,
        prices: Prices,
        labels: Set[Label],
        dish_type: str,
    ):
        self.name = name
        self.prices = prices
        self.labels = labels
        self.dish_type = dish_type

    def __repr__(self):
        return f"{self.name} {str(sorted(self.labels))}: {str(self.prices)}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self.name == other.name
                and self.prices == other.prices
                and self.labels == other.labels
                and self.dish_type == other.dish_type
            )
        return False

    def to_json_obj(self):
        return {
            "name": self.name,
            "prices": self.prices.to_json_obj(),
            "labels": sorted(map(lambda l: l.name, self.labels)),
            "dish_type": self.dish_type,
        }

    def __hash__(self) -> int:
        # http://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
        return (hash(self.name) << 1) ^ hash(self.prices) ^ hash(frozenset(self.labels)) ^ hash(self.dish_type)


class Menu:
    menu_date: datetime.date
    dishes: List[Dish]

    def __init__(self, menu_date: datetime.date, dishes: List[Dish]):
        self.menu_date = menu_date
        self.dishes = dishes

    def __repr__(self):
        return str(self.menu_date) + ": " + str(self.dishes)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            dishes_equal = set(self.dishes) == set(other.dishes)
            date_equal = self.menu_date == other.menu_date
            return dishes_equal and date_equal
        return False

    def remove_duplicates(self):
        unique: List[Dish] = []
        seen: Set[Dish] = set()

        for dish in self.dishes:
            if dish not in seen:
                unique.append(dish)
                seen.add(dish)

        self.dishes = unique


class Week:
    calendar_week: int
    year: int
    days: List[Menu]

    def __init__(self, calendar_week: int, year: int, days: List[Menu]):
        self.calendar_week = calendar_week
        self.year = year
        self.days = days

    def __repr__(self):
        week_str = f"Week {self.year}-{self.calendar_week}"
        for day in self.days:
            week_str += f"\n {day}"
        return week_str

    def to_json_obj(self):
        return {
            "number": self.calendar_week,
            "year": self.year,
            "days": [
                {"date": str(menu.menu_date), "dishes": [dish.to_json_obj() for dish in menu.dishes]}
                for menu in self.days
            ],
        }

    @staticmethod
    def to_weeks(menus: Dict[datetime.date, Menu]) -> Dict[int, Week]:
        weeks: Dict[int, Week] = {}
        if menus:
            for menu_key in menus:
                menu: Menu = menus[menu_key]
                menu_date = menu.menu_date
                # get calendar week
                calendar_week = menu_date.isocalendar()[1]
                # get year of the calendar week. watch out that for instance jan 01 can still be in week 52 of the
                # previous year
                year_of_calendar_week = (
                    menu_date.year - 1 if calendar_week == 52 and menu_date.month == 1 else menu_date.year
                )

                # append menus to respective week
                week: Week = weeks.get(calendar_week, Week(calendar_week, year_of_calendar_week, []))
                week.days.append(menu)
                weeks[calendar_week] = week
        return weeks

    @staticmethod
    def get_non_weekend_days_for_calendar_week(year: int, calendar_week: int) -> List[datetime.date]:
        days = []

        start_date = datetime.date.fromisocalendar(year, calendar_week, 1)
        for _ in range(5):
            days += [start_date]
            start_date += datetime.timedelta(days=1)
        return days
