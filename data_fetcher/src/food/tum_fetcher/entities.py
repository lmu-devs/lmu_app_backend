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
