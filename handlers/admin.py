import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_VERSION, ADMIN_IDS
from downloader import DOWNLOAD_CACHE

router = Router()
START_TIME = time.time()


def format_uptime(seconds: float) -> str:
    """Ish vaqtini chiroyli formatlash."""
    mins, sec = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f"{days} kun {hours} soat {mins} daqiqa"
    if hours > 0:
        return f"{hours} soat {mins} daqiqa {sec} soniya"
    return f"{mins} daqiqa {sec} soniya"


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """Bot tezligi va server javob berish vaqtini o'lchash."""
    start_ts = time.time()
    msg = await message.answer("🏓 <b>Pong...</b>", parse_mode="HTML")
    latency = (time.time() - start_ts) * 1000

    uptime_str = format_uptime(time.time() - START_TIME)
    active_cache = len(DOWNLOAD_CACHE)

    await msg.edit_text(
        f"🏓 <b>Pong!</b>\n\n"
        f"⚡ <b>Tezlik (Ping):</b> <code>{latency:.1f} ms</code>\n"
        f"⏱ <b>Ish vaqti:</b> <code>{uptime_str}</code>\n"
        f"📦 <b>Keshdagi fayllar:</b> <code>{active_cache} ta</code>\n"
        f"🤖 <b>Versiya:</b> <code>v{BOT_VERSION}</code>\n"
        f"🌐 <b>Holat:</b> <i>24/7 Serverda faol</i>",
        parse_mode="HTML"
    )
