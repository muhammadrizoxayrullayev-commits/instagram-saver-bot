import uuid
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from downloader import extract_instagram_url, download_video
from keyboards import get_video_inline_keyboard
from config import MAX_FILE_SIZE_MB

router = Router()


def format_duration(seconds: int) -> str:
    """Soniyalarni MM:SS yoki HH:MM:SS formatiga o'tkazadi."""
    if not seconds or seconds <= 0:
        return "Noma'lum"
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """Fayl hajmini MB da ko'rsatadi."""
    mb = size_bytes / (1024 * 1024)
    return f"{mb:.1f} MB"


@router.message(F.text)
async def handle_instagram_message(message: Message):
    """Instagram havolasini qabul qilish va videoni yuklab yuborish."""
    text = message.text or ""
    url = extract_instagram_url(text)

    # Agar xabarda Instagram havolasi bo'lmasa, e'tiborsiz qoldiramiz (yoki yordam beramiz)
    if not url:
        if "instagram.com" in text.lower() or "instagr.am" in text.lower():
            await message.reply(
                "⚠️ <b>Instagram havolasi noto'g'ri ko'rinishda!</b>\n\n"
                "Iltimos, havolani to'liq formatda (masalan, <code>https://www.instagram.com/reel/...</code>) yuboring.",
                parse_mode="HTML"
            )
        return

    # Jarayon boshlanganini foydalanuvchiga chiroyli bildirish
    status_msg = await message.reply(
        "⚡ <b>Instagram havolasi aniqlandi!</b>\n"
        "⏳ <i>Video serverga yuklanmoqda, iltimos kuting...</i>",
        parse_mode="HTML"
    )

    task_id = uuid.uuid4().hex[:10]

    try:
        # Videoni asinxron yuklab olish
        media_info = await download_video(url, task_id)

        # Hajmini tekshirish
        size_mb = media_info.file_size_bytes / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            await status_msg.edit_text(
                f"⚠️ <b>Fayl hajmi juda katta ({size_mb:.1f} MB)!</b>\n\n"
                f"Telegram botlari orqali faqat {MAX_FILE_SIZE_MB} MB gacha bo'lgan videolarni yuborish mumkin.",
                parse_mode="HTML"
            )
            return

        # Statusni yangilash
        await status_msg.edit_text(
            "📤 <b>Video tayyor!</b>\n"
            "🚀 <i>Telegramga yuborilmoqda...</i>",
            parse_mode="HTML"
        )

        # Sifatli va zamonaviy tavsif matni
        duration_str = format_duration(media_info.duration)
        size_str = format_file_size(media_info.file_size_bytes)
        
        caption = (
            f"🎬 <b>Instagram Video</b>\n\n"
            f"📝 <b>Tavsif:</b> <i>{media_info.title}</i>\n\n"
            f"👤 <b>Muallif:</b> @{media_info.uploader}\n"
            f"⏱ <b>Davomiyligi:</b> {duration_str}\n"
            f"💾 <b>Hajmi:</b> {size_str}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎵 <i>Ushbu videodagi musiqani yuklab olish uchun pastdagi tugmani bosing:</i>"
        )

        video_file = FSInputFile(media_info.video_path)
        keyboard = get_video_inline_keyboard(task_id, media_info.url)

        # Videoni yuborish
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML",
            supports_streaming=True
        )

        # Status xabarini o'chirib yuborish (chat toza bo'lishi uchun)
        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        err_text = str(e).lower()
        if "login required" in err_text or "private" in err_text:
            error_message = (
                "🔒 <b>Ushbu post yoki profil yopiq (Private)!</b>\n\n"
                "Faqat ommaviy (Public) profil va postlarni yuklab olish mumkin."
            )
        else:
            error_message = (
                "❌ <b>Videoni yuklab olishda xatolik yuz berdi.</b>\n\n"
                "Iltimos, quyidagilarni tekshiring:\n"
                "• Havola to'g'ri nusxalanganmi\n"
                "• Video Instagramda hali ham mavjudmi\n"
                "• Bir necha daqiqadan so'ng qayta urinib ko'ring."
            )

        try:
            await status_msg.edit_text(error_message, parse_mode="HTML")
        except Exception:
            await message.reply(error_message, parse_mode="HTML")
