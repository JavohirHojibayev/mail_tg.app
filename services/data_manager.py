import logging
import json
from pathlib import Path
from services.db_service import DBService
from utils.translit import matches_query

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
        - Katta-kichik harf farqsiz (case-insensitive)
        - Lotin va Krill yozuvlariga to'liq moslashgan (transliteratsiya)
        - x va h almashtirishlariga bardoshli
        """
        all_users = self.get_all_users_raw()
        if not all_users:
            return []

        if not search:
            return all_users

        search_clean = search.strip()
        matched = []
        for u in all_users:
            name = u.get("name", "")
            email = u.get("email", "")

            if (matches_query(name, search_clean) or
                matches_query(email.split("@")[0], search_clean) or
                matches_query(email, search_clean)):
                matched.append(u)

        return matched

    def refresh_from_db(self) -> bool:
        """Server bazasidan ma'lumotlarni qayta o'qib keshni yangilaydi"""
        if self.db.is_available():
            users = self.db.get_users()
            if users:
                self._save_cache(users)
                return True
        return False

    def refresh_cache(self) -> bool:
        """Alias for refresh_from_db"""
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
