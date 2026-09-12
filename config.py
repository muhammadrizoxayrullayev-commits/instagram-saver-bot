import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ID ro'yxati
admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]

# Fayl hajmi va vaqtinchalik parametrlar
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
TEMP_EXPIRE_MINUTES = int(os.getenv("TEMP_EXPIRE_MINUTES", "15"))

# Yuklab olish kataloglari
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Bot versiyasi va nomi
BOT_VERSION = "2.0.0"
BOT_AUTHOR = "Muhammadyusuf"
