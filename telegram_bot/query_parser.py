"""Parse natural language travel queries in Russian."""
import re
from datetime import datetime, date, timedelta


# City name → (IATA code, Russian display name, English name for Booking)
CITIES = {
    "москва":           ("MOW", "Москва",             "Moscow"),
    "москве":           ("MOW", "Москва",             "Moscow"),
    "москвы":           ("MOW", "Москва",             "Moscow"),
    "москву":           ("MOW", "Москва",             "Moscow"),
    "питер":            ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "питере":           ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "петербург":        ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "петербурге":       ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "санкт-петербург":  ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "санкт петербург":  ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "спб":              ("LED", "Санкт-Петербург",    "Saint Petersburg"),
    "казань":           ("KZN", "Казань",             "Kazan"),
    "казани":           ("KZN", "Казань",             "Kazan"),
    "казань":           ("KZN", "Казань",             "Kazan"),
    "екатеринбург":     ("SVX", "Екатеринбург",       "Yekaterinburg"),
    "екатеринбурге":    ("SVX", "Екатеринбург",       "Yekaterinburg"),
    "екб":              ("SVX", "Екатеринбург",       "Yekaterinburg"),
    "новосибирск":      ("OVB", "Новосибирск",        "Novosibirsk"),
    "новосибирске":     ("OVB", "Новосибирск",        "Novosibirsk"),
    "новосиб":          ("OVB", "Новосибирск",        "Novosibirsk"),
    "сочи":             ("AER", "Сочи",               "Sochi"),
    "краснодар":        ("KRR", "Краснодар",          "Krasnodar"),
    "ростов":           ("ROV", "Ростов-на-Дону",     "Rostov-on-Don"),
    "нижний новгород":  ("GOJ", "Нижний Новгород",    "Nizhny Novgorod"),
    "нижнем новгороде": ("GOJ", "Нижний Новгород",    "Nizhny Novgorod"),
    "нижний":           ("GOJ", "Нижний Новгород",    "Nizhny Novgorod"),
    "самара":           ("KUF", "Самара",             "Samara"),
    "уфа":              ("UFA", "Уфа",                "Ufa"),
    "уфе":              ("UFA", "Уфа",                "Ufa"),
    "воронеж":          ("VOZ", "Воронеж",            "Voronezh"),
    "пермь":            ("PEE", "Пермь",              "Perm"),
    "перми":            ("PEE", "Пермь",              "Perm"),
    "красноярск":       ("KJA", "Красноярск",         "Krasnoyarsk"),
    "иркутск":          ("IKT", "Иркутск",            "Irkutsk"),
    "иркутске":         ("IKT", "Иркутск",            "Irkutsk"),
    "владивосток":      ("VVO", "Владивосток",        "Vladivostok"),
    "хабаровск":        ("KHV", "Хабаровск",          "Khabarovsk"),
    "минводы":          ("MRV", "Мин. Воды",          "Mineralnye Vody"),
    "минеральные воды": ("MRV", "Мин. Воды",          "Mineralnye Vody"),
    "анапа":            ("AAQ", "Анапа",              "Anapa"),
    "калининград":      ("KGD", "Калининград",        "Kaliningrad"),
    "тюмень":           ("TJM", "Тюмень",             "Tyumen"),
    "омск":             ("OMS", "Омск",               "Omsk"),
    "волгоград":        ("VOG", "Волгоград",          "Volgograd"),
    "мурманск":         ("MMK", "Мурманск",           "Murmansk"),
    "сургут":           ("SGC", "Сургут",             "Surgut"),
    "томск":            ("TOF", "Томск",              "Tomsk"),
    "тюмень":           ("TJM", "Тюмень",             "Tyumen"),
    "баку":             ("GYD", "Баку",               "Baku"),
    "ереван":           ("EVN", "Ереван",             "Yerevan"),
    "тбилиси":          ("TBS", "Тбилиси",            "Tbilisi"),
    "ташкент":          ("TAS", "Ташкент",            "Tashkent"),
    "алматы":           ("ALA", "Алматы",             "Almaty"),
    "алма-ата":         ("ALA", "Алматы",             "Almaty"),
    "бишкек":           ("FRU", "Бишкек",             "Bishkek"),
    "дубай":            ("DXB", "Дубай",              "Dubai"),
    "дубаи":            ("DXB", "Дубай",              "Dubai"),
    "анталья":          ("AYT", "Анталья",            "Antalya"),
    "анталия":          ("AYT", "Анталья",            "Antalya"),
    "стамбул":          ("IST", "Стамбул",            "Istanbul"),
    "бангкок":          ("BKK", "Бангкок",            "Bangkok"),
    "пхукет":           ("HKT", "Пхукет",             "Phuket"),
    "берлин":           ("BER", "Берлин",             "Berlin"),
    "париж":            ("CDG", "Париж",              "Paris"),
    "рим":              ("FCO", "Рим",                "Rome"),
    "мадрид":           ("MAD", "Мадрид",             "Madrid"),
    "барселона":        ("BCN", "Барселона",          "Barcelona"),
    "барселоне":        ("BCN", "Барселона",          "Barcelona"),
    "лондон":           ("LHR", "Лондон",             "London"),
    "амстердам":        ("AMS", "Амстердам",          "Amsterdam"),
    "вена":             ("VIE", "Вена",               "Vienna"),
    "прага":            ("PRG", "Прага",              "Prague"),
    "варшава":          ("WAW", "Варшава",            "Warsaw"),
    "милан":            ("MXP", "Милан",              "Milan"),
    "мюнхен":           ("MUC", "Мюнхен",            "Munich"),
    "франкфурт":        ("FRA", "Франкфурт",         "Frankfurt"),
    "токио":            ("NRT", "Токио",              "Tokyo"),
    "пекин":            ("PEK", "Пекин",              "Beijing"),
    "шанхай":           ("PVG", "Шанхай",             "Shanghai"),
    "нью-йорк":         ("JFK", "Нью-Йорк",          "New York"),
}

MONTH_MAP = {
    "января": 1,  "январе": 1,  "январь": 1,  "янв": 1,
    "февраля": 2, "феврале": 2, "февраль": 2, "фев": 2,
    "марта": 3,   "марте": 3,   "март": 3,    "мар": 3,
    "апреля": 4,  "апреле": 4,  "апрель": 4,  "апр": 4,
    "мая": 5,     "мае": 5,     "май": 5,
    "июня": 6,    "июне": 6,    "июнь": 6,    "июн": 6,
    "июля": 7,    "июле": 7,    "июль": 7,    "июл": 7,
    "августа": 8, "августе": 8, "август": 8,  "авг": 8,
    "сентября": 9,  "сентябре": 9,  "сентябрь": 9,  "сен": 9,  "сент": 9,
    "октября": 10,  "октябре": 10,  "октябрь": 10,  "окт": 10,
    "ноября": 11,   "ноябре": 11,   "ноябрь": 11,   "ноя": 11,
    "декабря": 12,  "декабре": 12,  "декабрь": 12,  "дек": 12,
}


def find_cities(text: str) -> list[tuple]:
    """Return list of (iata, ru_name, en_name) found in text, ordered by position in text."""
    text_lower = text.lower()
    found = {}    # iata -> info
    positions = {}  # iata -> first position in text

    # Longer city names take priority over shorter ones (e.g. "нижний новгород" over "нижний")
    for city_word, info in sorted(CITIES.items(), key=lambda x: -len(x[0])):
        idx = text_lower.find(city_word)
        if idx != -1 and info[0] not in found:
            found[info[0]] = info
            positions[info[0]] = idx

    # Sort by position so the first-mentioned city becomes origin
    return [info for _, info in sorted(found.items(), key=lambda x: positions[x[0]])]


def find_dates(text: str) -> tuple[date | None, date | None]:
    """Return (depart_date, return_date) parsed from Russian text."""
    text_lower = text.lower()
    today = date.today()
    depart = None
    ret = None

    if "послезавтра" in text_lower:
        depart = today + timedelta(days=2)
        return depart, None
    if "завтра" in text_lower:
        depart = today + timedelta(days=1)
        return depart, None

    month_pattern = "(" + "|".join(sorted(MONTH_MAP.keys(), key=len, reverse=True)) + ")"
    # Range: "12-14 марта" or "12–17 марта"
    range_pat = re.compile(
        r'(\d{1,2})\s*[-–—]\s*(\d{1,2})\s+' + month_pattern, re.IGNORECASE
    )
    m = range_pat.search(text_lower)
    if m:
        month_num = MONTH_MAP.get(m.group(3), 0)
        if month_num:
            year = today.year
            d1, d2 = int(m.group(1)), int(m.group(2))
            try:
                if date(year, month_num, d1) < today:
                    year += 1
                depart = date(year, month_num, d1)
                ret = date(year, month_num, d2)
            except ValueError:
                pass
            return depart, ret

    # Single date: "15 марта"
    single_pat = re.compile(r'(\d{1,2})\s+' + month_pattern, re.IGNORECASE)
    m = single_pat.search(text_lower)
    if m:
        month_num = MONTH_MAP.get(m.group(2), 0)
        if month_num:
            year = today.year
            day = int(m.group(1))
            try:
                d = date(year, month_num, day)
                if d < today:
                    d = date(year + 1, month_num, day)
                depart = d
            except ValueError:
                pass

    # Look for "N ночей/ночи/дней" to derive return date
    nights_m = re.search(r'(\d+)\s*(ноч|дне|дней)', text_lower)
    if depart and nights_m:
        nights = int(nights_m.group(1))
        ret = depart + timedelta(days=nights)

    return depart, ret


NUM_WORDS = {
    "один": 1, "одного": 1, "одному": 1, "одна": 1,
    "два": 2, "двух": 2, "двое": 2, "двоих": 2, "двум": 2,
    "три": 3, "трёх": 3, "трое": 3, "троих": 3, "трем": 3, "трём": 3,
    "четыре": 4, "четырёх": 4, "четырех": 4, "четверо": 4,
    "пять": 5, "пятеро": 5, "пяти": 5,
    "шесть": 6, "шести": 6, "шестеро": 6,
    "семь": 7, "семи": 7,
    "восемь": 8, "восьми": 8,
    "девять": 9,
    "десять": 10,
}

CABIN_MAP = {
    "бизнес": "C",
    "бизнес-класс": "C",
    "бизнес класс": "C",
    "бизнесклас": "C",
    "первый класс": "F",
    "первого класса": "F",
    "первый": "F",
    "эконом": "Y",
    "эконом-класс": "Y",
    "эконом класс": "Y",
    "комфорт": "W",
    "комфорт-класс": "W",
    "премиум эконом": "W",
    "премиум-эконом": "W",
}


def find_passengers(text: str) -> int:
    """Extract number of passengers from text. Returns 1 if not found."""
    t = text.lower()

    # «на 2 человек», «для 3 пассажиров», «2 взрослых», «2 места»
    digit_pat = re.compile(
        r'(?:на|для|нас|вдвоем|втроем)?\s*(\d+)\s*'
        r'(?:человек|чел\.?|пассажир|взрослых|взрослых|места|билет[аов]?)'
    )
    m = digit_pat.search(t)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 9:
            return n

    # Word-based: «двое человек», «трое взрослых»
    for word, num in NUM_WORDS.items():
        pat = re.compile(
            r'\b' + re.escape(word) + r'\b\s*'
            r'(?:человек|чел\.?|пассажир|взрослых|места|билет[аов]?)?'
        )
        if pat.search(t):
            return num

    # «вдвоём», «втроём», «вчетвером» etc.
    group_map = {
        "вдвоем": 2, "вдвоём": 2,
        "втроем": 3, "втроём": 3,
        "вчетвером": 4, "впятером": 5,
    }
    for word, num in group_map.items():
        if word in t:
            return num

    return 1


def find_cabin(text: str) -> str:
    """Detect cabin class. Returns 'Y' (economy) by default."""
    t = text.lower()
    # Sort by length desc to match longer phrases first
    for phrase, code in sorted(CABIN_MAP.items(), key=lambda x: -len(x[0])):
        if phrase in t:
            return code
    return "Y"


def detect_type(text: str) -> str:
    """Detect search type: flight, hotel, train, combo."""
    t = text.lower()
    has_hotel = any(w in t for w in ["отель", "гостиниц", "ночей", "ночи", "проживан", "хостел"])
    has_train = any(w in t for w in ["поезд", "сапсан", "ласточка", "ржд", "ж/д", "жд", "купе", "плацкарт"])
    has_flight = any(w in t for w in ["авиа", "самолет", "рейс", "перелет", "авиабилет", "билет"])
    if has_train:
        return "train"
    if has_hotel and not has_flight:
        return "hotel"
    if has_hotel and has_flight:
        return "combo"
    return "flight"


def parse_query(text: str) -> dict:
    """Parse full travel query. Returns dict with origin, destination, dates, type, passengers, cabin."""
    cities = find_cities(text)
    depart, ret = find_dates(text)
    q_type = detect_type(text)
    passengers = find_passengers(text)
    cabin = find_cabin(text)

    result = {
        "type": q_type,
        "cities": cities,
        "depart": depart,
        "return": ret,
        "passengers": passengers,
        "cabin": cabin,
        "raw": text,
    }

    if len(cities) >= 2:
        result["origin"] = cities[0]
        result["destination"] = cities[1]
    elif len(cities) == 1:
        result["destination"] = cities[0]
        result["origin"] = ("MOW", "Москва", "Moscow")

    return result
