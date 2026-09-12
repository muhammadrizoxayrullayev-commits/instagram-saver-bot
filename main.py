import asyncio
import logging
import sys
from pathlib import Path

# Windows konsolida emojilar to'g'ri chiqishi uchun UTF-8 ga moslash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiohttp import web
from config import BOT_TOKEN, BOT_VERSION, DOWNLOADS_DIR
from downloader import cleanup_expired_files, FFMPEG_PATH
from handlers import start, instagram, callbacks, admin

# Log sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("InstagramBot")


async def health_check(request):
    """Render uchun 24/7 jonli tekshiruv (health check)."""
    return web.Response(text="Instagram Saver Bot 24/7 is Active!")


async def start_web_server():
    """Render bulutida bepul ishlashi uchun portni ochish."""
    port_str = os.getenv("PORT")
    if not port_str:
        return
    try:
        port = int(port_str)
        app = web.Application()
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Render Web Server port {port} da muvaffaqiyatli ishga tushdi.")
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda xatolik: {e}")


async def main():
    """Botning asosiy ishga tushish funksiyasi."""
    print("=" * 60)
    print(f"🚀 Instagram Media & Music Downloader Bot v{BOT_VERSION}")
    print(f"📂 Yuklab olish papkasi: {DOWNLOADS_DIR}")
    print(f"🎬 FFmpeg yo'li: {FFMPEG_PATH}")
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

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash (tartib muhim: aniq komandalar birinchi)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(callbacks.router)
    dp.include_router(instagram.router)

    # Vaqtinchalik keshni tozalash fon vazifasini ishga tushirish
    asyncio.create_task(cleanup_expired_files())

    # Agar Render yoki boshqa hostingda bo'lsa, web serverni ishga tushirish
    asyncio.create_task(start_web_server())

    # Bot ma'lumotlarini olish
    try:
        bot_user = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_user.username} ({bot_user.first_name})")
        print(f"✅ Bot Telegramda faol: https://t.me/{bot_user.username}")
        print("💡 Noutbukingizni o'chirganda ham 24/7 ishlashi uchun DEPLOY_GUIDE_UZ.md ni o'qing.")
    except Exception as e:
        logger.error(f"Telegram API bilan ulanishda xatolik: {e}")
        return

    # Pollingni ishga tushirish
    try:
        # Avvalgi to'planib qolgan eskirgan xabarlarni o'chirish (drop_pending_updates=True)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
