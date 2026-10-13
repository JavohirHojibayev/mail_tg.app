import os
from pathlib import Path
from dotenv import load_dotenv

# .env yuklash
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8875078214:AAFJZgddl_Rm5E21SjfUR36FvpZJRvt9lWI")

# Mail Server & API sozlamalari
MAIL_SERVER = os.getenv("MAIL_SERVER", "mail.uz-potash.uz")
MAIL_DOMAIN = os.getenv("MAIL_DOMAIN", "uz-potash.uz")
API_BASE_URL = os.getenv("API_BASE_URL", "https://mail.uz-potash.uz")

# Korporativ xodim akkaunti (API orqali avtomatik login qilish uchun, ixtiyoriy)
CORP_USER = os.getenv("CORP_USER", "")
CORP_PASSWORD = os.getenv("CORP_PASSWORD", "")

# PostgreSQL sozlamalari (iRedMail vmail bazasi)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "vmail")
DB_USER = os.getenv("DB_USER", "vmailadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Sahifalash (bir sahifada nechta xodim ko'rsatiladi)
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "8"))
