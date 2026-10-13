import logging
import requests
import urllib3
import config

# SSL sertifikati (self-signed bo'lsa ogohlantirishni o'chirish)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

class ApiService:
    def __init__(self):
        self.base_url = config.API_BASE_URL.rstrip('/')
        self.token = None

    def login(self, email: str, password: str) -> tuple[bool, str]:
        """
        Korporativ email va parol bilan backend API ga kirish.
        Muvaffaqiyatli bo'lsa JWT tokenni saqlab oladi.
        """
        if not email or not password:
            return False, "Email va parol kiritilmagan"

        clean_email = email.strip().lower()
        if '@' not in clean_email:
            clean_email = f"{clean_email}@{config.MAIL_DOMAIN}"

        url = f"{self.base_url}/api/auth/login"
        try:
            resp = requests.post(
                url,
                json={"email": clean_email, "password": password},
                verify=False,
                timeout=10
            )
            data = resp.json()
            if resp.status_code == 200 and data.get("success"):
                self.token = data.get("token")
                return True, data.get("message", "Kirish muvaffaqiyatli!")
            else:
                return False, data.get("message", "Email yoki parol noto'g'ri")
        except Exception as e:
            logger.error(f"API login xatosi: {e}")
            return False, f"Serverga ulanishda xatolik: {str(e)}"

    def get_users(self, search: str = None, department: str = None) -> list:
        """API orqali xodimlar ro'yxatini oladi"""
        if not self.token and config.CORP_USER and config.CORP_PASSWORD:
            self.login(config.CORP_USER, config.CORP_PASSWORD)

        if not self.token:
            return []

        url = f"{self.base_url}/api/users"
        params = {"limit": 300}
        if search:
            params["search"] = search
        if department:
            params["department"] = department

        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data.get("users", [])
            elif resp.status_code == 401:
                # Token eskirgan bo'lsa qayta login
                if config.CORP_USER and config.CORP_PASSWORD:
                    ok, _ = self.login(config.CORP_USER, config.CORP_PASSWORD)
                    if ok:
                        headers["Authorization"] = f"Bearer {self.token}"
                        r2 = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
                        if r2.status_code == 200 and r2.json().get("success"):
                            return r2.json().get("users", [])
            return []
        except Exception as e:
            logger.error(f"API get_users xatosi: {e}")
            return []

    def get_departments(self) -> list:
        """API orqali bo'limlar ro'yxatini oladi"""
        if not self.token and config.CORP_USER and config.CORP_PASSWORD:
            self.login(config.CORP_USER, config.CORP_PASSWORD)

        if not self.token:
            return []

        url = f"{self.base_url}/api/users/departments"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(url, headers=headers, verify=False, timeout=10)
            if resp.status_code == 200 and resp.json().get("success"):
                return resp.json().get("departments", [])
            return []
        except Exception as e:
            logger.error(f"API get_departments xatosi: {e}")
            return []
