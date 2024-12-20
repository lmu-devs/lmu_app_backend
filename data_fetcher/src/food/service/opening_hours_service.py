from datetime import time
from shared.src.schemas import OpeningHours, OpeningHour, WeekdayEnum

# Mensa Leopoldstraße
leopold_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)

# StuCafé Leopoldstraße
stucafe_leopold_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)


# StuLounge Leopoldstraße
stulounge_leopold_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)


# StuBistroMensa Oettingenstraße
oettingenstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(14, 30)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 30)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 30)),
    ],
    lecture_free_serving_hours=None,
)


# StuBistroMensa Adalbertstraße
adalbertstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)


# Espressobar Ludwigstraße
espressobar_ludwig_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(18, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(18, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(18, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(18, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(18, 0)),
        OpeningHour(day=WeekdayEnum.SATURDAY, start_time=time(9, 0), end_time=time(18, 0)),
    ],
    serving_hours=None, 
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)


# StuBistroMensa Akademiestraße
akademiestr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
)


# StuBistro Schellingstraße
schellingstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)

# StuBistroMensa Schillerstraße (currently closed)
schillerstr_opening_hours = OpeningHours(
    opening_hours=None,
    serving_hours=None,
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)


# StuBistro Goethestraße
goethestr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)

# Mensa Arcisstraße
arcisstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 30)),
    ],
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)

# StuLounge Arcisstraße
stulounge_arcis_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)

# StuBistro Arcisstraße
stubistro_arcis_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(15, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=None,
)


# StuCafe Arcisstraße
stucafe_arcisstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 0), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 0), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 0), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 0), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 0), end_time=time(15, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 0)),
    ],
    lecture_free_serving_hours=None,
)


# StuBistro Mensa Bernd Eichinger Platz
eichinger_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 30), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 30), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 30), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 30), end_time=time(16, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 30), end_time=time(15, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 0)),
    ],
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)


# StuBistroMensa am Olympiacampus
olympiacampus_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    serving_hours=None,  # No specific serving hours mentioned
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None
)


# StuLounge am Olympiacampus
stulounge_olympia_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(16, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(16, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(16, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(16, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(15, 30)),
    ],
    serving_hours=None,  # No specific serving hours mentioned
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 30), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 30), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 30), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 30), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 30), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)   


# Mensa Lothstraße
lothstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 30)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(14, 0)),
    ],
    serving_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(11, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(11, 0), end_time=time(13, 30)),
    ],
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)


# StuCafé Lothstraße
stucafe_loth_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(9, 0), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(9, 0), end_time=time(14, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(10, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(10, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(10, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(10, 0), end_time=time(14, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(10, 0), end_time=time(14, 0)),
    ],
    lecture_free_serving_hours=None,
)



# StuCafe Karlstraße
karlstr_opening_hours = OpeningHours(
    opening_hours=[
        OpeningHour(day=WeekdayEnum.MONDAY, start_time=time(8, 15), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.TUESDAY, start_time=time(8, 15), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.WEDNESDAY, start_time=time(8, 15), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.THURSDAY, start_time=time(8, 15), end_time=time(15, 0)),
        OpeningHour(day=WeekdayEnum.FRIDAY, start_time=time(8, 15), end_time=time(15, 0)),
    ],
    serving_hours=None,
    lecture_free_hours=None,
    lecture_free_serving_hours=None,
)




