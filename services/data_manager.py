import logging
import json
from pathlib import Path
from services.db_service import DBService
from services.api_service import ApiService

logger = logging.getLogger(__name__)

CACHE_FILE = Path(__file__).resolve().parent.parent / "users_cache.json"

class DataManager:
    def __init__(self):
        self.db = DBService()
        self.api = ApiService()
        self._user_tokens = {}  # telegram_chat_id -> user specific token

    def authenticate_user(self, chat_id: int, email: str, password: str) -> tuple[bool, str]:
        """Foydalanuvchi o'z korporativ pochtasi orqali tizimga kiradi"""
        ok, msg = self.api.login(email, password)
        if ok and self.api.token:
            self._user_tokens[chat_id] = self.api.token
            # Xodimlarni yangilab keshga saqlash
            self.refresh_cache()
        return ok, msg

    def is_user_authenticated(self, chat_id: int) -> bool:
        return chat_id in self._user_tokens or bool(self.api.token)

    def get_users(self, search: str = None, department: str = None) -> list:
        """
        Xodimlarni bir nechta manbadan izlaydi:
        1. PostgreSQL to'g'ridan-to'g'ri (eng tezkor)
        2. Backend REST API
        3. Mahalliy JSON kesh
        """
        # 1. DB orqali tekshirish
        if self.db.is_available():
            users = self.db.get_users(search=search, department=department)
            if users:
                self._save_cache(users)
                return users

        # 2. API orqali tekshirish
        users = self.api.get_users(search=search, department=department)
        if users:
            self._save_cache(users)
            return users

        # 3. Keshdan o'qish (offline fallback)
        cached = self._load_cache()
        if cached:
            filtered = cached
            if department:
                filtered = [u for u in filtered if u.get("department") == department]
            if search:
                s = search.lower()
                filtered = [
                    u for u in filtered
                    if s in u.get("name", "").lower()
                    or s in u.get("email", "").lower()
                    or s in u.get("department", "").lower()
                    or s in u.get("position", "").lower()
                ]
            return filtered

        return []

    def get_departments(self) -> list:
        """Bo'limlar ro'yxatini olish"""
        if self.db.is_available():
            deps = self.db.get_departments()
            if deps:
                return deps

        deps = self.api.get_departments()
        if deps:
            return deps

        # Keshdan bo'limlarni ajratish
        cached = self._load_cache()
        dept_set = {u.get("department") for u in cached if u.get("department")}
        return sorted(list(dept_set))

    def refresh_cache(self):
        """Keshni yangilaydi"""
        users = []
        if self.db.is_available():
            users = self.db.get_users()
        elif self.api.token:
            users = self.api.get_users()
        if users:
            self._save_cache(users)

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
