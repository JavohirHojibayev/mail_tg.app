import logging
import json
from pathlib import Path
from services.db_service import DBService
from utils.translit import calculate_match_score

logger = logging.getLogger(__name__)

CACHE_FILE = Path(__file__).resolve().parent.parent / "users_cache.json"

class DataManager:
    def __init__(self):
        self.db = DBService()

    def get_all_users_raw(self) -> list:
        """Barcha mavjud xodimlarni Kesh yoki DB dan yig'adi"""
        cached = self._load_cache()
        if cached:
            return cached

        if self.db.is_available():
            users = self.db.get_users()
            if users:
                self._save_cache(users)
                return users

        return []

    def get_users(self, search: str = None) -> list:
        """
        Xodimlarni qidirish:
        - Ism + familiya yozilganda ham ism, ham familiya bo'yicha topadi
        - Katta-kichik harf farqsiz (case-insensitive)
        - Lotin va Krill yozuvlariga to'liq moslashgan (transliteratsiya)
        - Eng mos kelgan xodimlar ball bo'yicha yuqorida chiqadi
        """
        all_users = self.get_all_users_raw()
        if not all_users:
            return []

        if not search:
            return all_users

        search_clean = search.strip()
        scored_users = []

        for u in all_users:
            score = calculate_match_score(u, search_clean)
            if score >= 20: # Moslik ostonasi
                scored_users.append((score, u))

        # Moslik darajasi bo'yicha saralash (eng moslari eng birinchi)
        scored_users.sort(key=lambda x: x[0], reverse=True)

        # Agar yuqori moslikdagi natijalar bo'lsa (masalan ism+familiya to'liq mos kelganlar),
        # faqat to'liq moslarini qoldiramiz (keraksiz qisman mosliklarni chiqarmaymiz)
        if scored_users and scored_users[0][0] >= 70:
            scored_users = [item for item in scored_users if item[0] >= 70]

        return [u for score, u in scored_users]

    def refresh_from_db(self) -> bool:
        """Server bazasidan ma'lumotlarni qayta o'qib keshni yangilaydi"""
        if self.db.is_available():
            users = self.db.get_users()
            if users:
                self._save_cache(users)
                return True
        return False

    def refresh_cache(self) -> bool:
        return self.refresh_from_db()

    def _save_cache(self, users: list):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Kesh saqlashda xatolik: {e}")

    def _load_cache(self) -> list:
        if not CACHE_FILE.exists():
            return []
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Kesh o'qishda xatolik: {e}")
            return []
