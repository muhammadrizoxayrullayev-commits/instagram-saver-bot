import asyncio
import logging
import os
import sys
from pathlib import Path

# Loyiha papkasini doimo asosiy ishchi katalog qilish
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)


class SafeStream:
    """Fon rejimida quvur uzilishi (WinError 233) yoki None stdout xatolarini bartaraf etadi."""
    def __init__(self, target_file, original_stream=None):
        self.target_file = target_file
        self.original_stream = original_stream

    def write(self, s):
        try:
            if self.original_stream and hasattr(self.original_stream, "write"):
                self.original_stream.write(s)
                return
        except Exception:
            pass
        try:
            with open(self.target_file, "a", encoding="utf-8", errors="replace") as f:
                f.write(s)
        except Exception:
            pass

    def flush(self):
        try:
            if self.original_stream and hasattr(self.original_stream, "flush"):
                self.original_stream.flush()
        except Exception:
            pass

    def reconfigure(self, *args, **kwargs):
        pass


sys.stdout = SafeStream(BASE_DIR / "bot.log", sys.stdout)
sys.stderr = SafeStream(BASE_DIR / "bot.log", sys.stderr)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import aiohttp
from aiohttp import web
from config import BOT_TOKEN, BOT_VERSION, DOWNLOADS_DIR
from downloader import cleanup_expired_files, FFMPEG_PATH
from handlers import start, instagram, callbacks, admin

# Log sozlamalari (konsolga va bot.log fayliga yoziladi)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("InstagramBot")


# Dispatcher va routerlarni faqat bir marta sozlash
dp = Dispatcher()
dp.include_router(admin.router)
dp.include_router(start.router)
dp.include_router(callbacks.router)
dp.include_router(instagram.router)

_background_tasks_started = False


async def health_check(request):
    """Render uchun 24/7 jonli tekshiruv (health check)."""
    return web.Response(text="Instagram Saver Bot 24/7 is Active!", status=200)


async def start_web_server():
    """Render bulutida bepul ishlashi uchun portni ochish."""
    try:
        port = int(os.getenv("PORT", "8085"))
        app = web.Application()
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Render Web Server 0.0.0.0:{port} da muvaffaqiyatli ishga tushdi.")
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda xatolik: {e}")


async def anti_sleep_ping():
    """Render va bulutli serverlarda 15 daqiqada uxlab qolmasligi uchun
    har 9 daqiqada o'z tashqi URL manziliga so'rov yuborib turadi (Self-Ping)."""
    await asyncio.sleep(60)  # Dastlab server to'liq ko'tarilishini kutamiz

    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PING_URL")
    if not url:
        logger.info("Anti-Sleep: RENDER_EXTERNAL_URL topilmadi (lokal rejimda ishlayapti).")
        return

    target = f"{url.rstrip('/')}/health"
    logger.info(f"Anti-Sleep (Self-Ping) tizimi faollashtirildi: {target}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(target, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    logger.info(f"Anti-Sleep: Server muvaffaqiyatli uyg'oq saqlandi (Status: {response.status})")
            except Exception as e:
                logger.warning(f"Anti-Sleep ping xatosi: {e}")

            # Render 15 daqiqada uxlab qoladi, shuning uchun har 9 daqiqada (540 soniya) chaqiramiz
            await asyncio.sleep(540)


async def main():
    """Botning asosiy ishga tushish funksiyasi."""
    global _background_tasks_started
    print("=" * 60)
    print(f"Instagram Media & Music Downloader Bot v{BOT_VERSION}")
    print(f"Yuklab olish papkasi: {DOWNLOADS_DIR}")
    print(f"FFmpeg yo'li: {FFMPEG_PATH}")
    print("=" * 60)

    # Token tekshiruvi
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "!" * 60 + "\n"
            "XATOLIK: BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, .env faylini oching va Telegram @BotFather dan olingan tokeningizni kiriting:\n"
            "BOT_TOKEN=1234567890:ABC-DEF...\n"
            + "!" * 60
        )
        return

    # Bot yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Fon vazifalarini faqat bir marta ishga tushirish
    if not _background_tasks_started:
        asyncio.create_task(cleanup_expired_files())
        asyncio.create_task(start_web_server())
        asyncio.create_task(anti_sleep_ping())
        _background_tasks_started = True

    # Bot ma'lumotlarini olish
    try:
        bot_user = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_user.username} ({bot_user.first_name})")
        print(f"Bot Telegramda faol: https://t.me/{bot_user.username}")
        print("Noutbukingizni o'chirganda ham 24/7 ishlashi uchun DEPLOY_GUIDE_UZ.md ni o'qing.")
    except Exception as e:
        logger.error(f"Telegram API bilan ulanishda xatolik: {e}")
        return

    # Pollingni ishga tushirish (handle_signals=False fon rejimida barqaror ishlashi uchun)
    try:
        # Avvalgi to'planib qolgan eskirgan xabarlarni o'chirish (drop_pending_updates=True)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, handle_signals=False)
    finally:
        await bot.session.close()


async def run_bot_with_auto_restart():
    """Tarmoq yoki API xatosi bo'lsa ham bot to'xtamasdan avtomatik qayta ulanadi."""
    while True:
        try:
            await main()
            # Agar BOT_TOKEN kiritilmagan bo'lsa to'xtaymiz
            if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
                break
            logger.warning("Bot asosiy sikli tugadi. 3 soniyadan so'ng qayta ishga tushiriladi...")
            await asyncio.sleep(3)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi.")
            break
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            logger.error(f"Kutilmagan xatolik yuz berdi:\n{err_msg}")
            try:
                with open(BASE_DIR / "crash.log", "a", encoding="utf-8") as f:
                    f.write(err_msg + "\n" + "="*40 + "\n")
            except Exception:
                pass
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot_with_auto_restart())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
    except Exception as e:
        import traceback
        with open(BASE_DIR / "crash.log", "a", encoding="utf-8") as f:
            f.write(traceback.format_exc() + "\n")


