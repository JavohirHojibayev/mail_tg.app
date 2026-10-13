"""
O'zbek tili Lotin-Krill transliteratsiyasi va qidiruvni normalizatsiya qilish moduli.
Katta-kichik harflar, apostroflar, x/h farqlari va krill/lotin yozuvlariga moslashgan.
"""

import re

# Krill -> Lotin lug'ati
CYR_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'x', 'ҳ': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sh',
    'ъ': "'", 'ь': "", 'э': 'e', 'ю': 'yu', 'я': 'ya', 'ў': "o'", 'ғ': "g'", 'қ': 'q'
}

# Lotin -> Krill birikmalari
LAT_COMBOS_TO_CYR = [
    ("o'", "ў"), ("oʻ", "ў"), ("o`", "ў"), ("o’", "ў"),
    ("g'", "ғ"), ("gʻ", "ғ"), ("g`", "ғ"), ("g’", "ғ"),
    ("sh", "ш"), ("ch", "ч"),
    ("yo", "ё"), ("yu", "ю"), ("ya", "я"), ("ts", "ц"),
    ("ye", "е"),
]

LAT_SINGLE_TO_CYR = {
    'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 'e': 'е',
    'j': 'ж', 'z': 'з', 'i': 'и', 'y': 'й', 'k': 'к', 'l': 'л', 'm': 'м',
    'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
    'f': 'ф', 'x': 'х', 'h': 'ҳ', 'q': 'қ'
}

def cyrillic_to_latin(text: str) -> str:
    """Krill matnni lotinga o'giradi"""
    if not text:
        return ""
    result = []
    text_lower = text.lower()
    for char in text_lower:
        result.append(CYR_TO_LAT.get(char, char))
    return "".join(result)

def latin_to_cyrillic(text: str) -> str:
    """Lotin matnni krillga o'giradi"""
    if not text:
        return ""
    res = text.lower()
    for lat, cyr in LAT_COMBOS_TO_CYR:
        res = res.replace(lat, cyr)
    chars = []
    for char in res:
        chars.append(LAT_SINGLE_TO_CYR.get(char, char))
    return "".join(chars)

def normalize_text(text: str) -> str:
    """
    Qidiruv uchun matnni tozalaydi va solishtirishga tayyorlaydi:
    1. Kichik harfga o'tkazadi
    2. Barcha turdagi apostroflarni (', `, ʻ, ʼ, ’) bitta standart ' ga keltiradi
    3. Krill bo'lsa lotinga o'giradi
    4. x va h farqini yumshatadi (ikkalasini ham h ga keltirib solishtirish osonlashadi)
    5. Ortiqcha belgilarni olib tashlaydi
    """
    if not text:
        return ""
    t = text.lower()
    # Har xil apostrof belgilarini bir xillashtirish
    t = re.sub(r"[`ʻʼ’']", "'", t)
    # Agar krill harflari bo'lsa lotinga o'girish
    t = cyrillic_to_latin(t)
    # x va h ni bitta formatga keltirish (o'zbek tilida tez-tez adashiladi)
    t_relaxed = t.replace("x", "h")
    # Probellarni tozalash
    t_relaxed = re.sub(r"\s+", " ", t_relaxed).strip()
    return t_relaxed

def matches_query(target: str, query: str) -> bool:
    """
    Katta-kichik, lotin-krill, x/h farqlaridan qat'iy nazar matn mos kelishini tekshiradi.
    Masalan:
    target: "Javohir Hojibayev"
    query: "javohir", "hojibayev", "жавоҳир", "жавохир хожибаев", "javoxir" -> HAMMASI TRUE
    """
    if not target or not query:
        return False

    norm_target = normalize_text(target)
    norm_query = normalize_text(query)

    # 1. To'g'ridan-to'g'ri qidiruv
    if norm_query in norm_target:
        return True

    # 2. So'zma-so'z qidiruv (barcha qidiruv so'zlari maqsadda bormi)
    query_words = norm_query.split()
    target_words = norm_target.split()

    if all(any(qw in tw for tw in target_words) for qw in query_words):
        return True

    # 3. Krillcha variantini ham solishtirib ko'rish
    cyr_target = latin_to_cyrillic(target.lower()).replace("х", "ҳ")
    cyr_query = latin_to_cyrillic(query.lower()).replace("х", "ҳ")
    if cyr_query in cyr_target:
        return True

    return False
