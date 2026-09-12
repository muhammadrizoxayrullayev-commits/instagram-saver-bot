from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from downloader import DOWNLOAD_CACHE, extract_audio
from keyboards import get_audio_inline_keyboard

router = Router()


@router.callback_query(F.data.startswith("audio:"))
async def cb_download_audio(callback: CallbackQuery):
    """Videodan musiqani (MP3) ajratib olib yuborish."""
    task_id = callback.data.split(":", 1)[1]
    
    # Keshdan topish
    media_info = DOWNLOAD_CACHE.get(task_id)

    if not media_info:
        await callback.answer(
            "⚠️ Ushbu video vaqti o'tib ketgan. Iltimos, havolani qayta yuboring.",
            show_alert=True
        )
        return

    # Foydalanuvchiga jarayon boshlanganini darhol ko'rsatish
    await callback.answer("🎵 Musiqa ajratib olinmoqda...")

    status_msg = await callback.message.reply(
        "🎧 <b>Musiqa ajratilmoqda...</b>\n"
        "⚡ <i>MP3 formatiga o'girilmoqda, iltimos kuting...</i>",
        parse_mode="HTML"
    )

    try:
        # Musiqani FFmpeg orqali tezkor ajratish
        audio_path = await extract_audio(media_info)

        audio_caption = (
            f"🎵 <b>Instagram Audio (MP3)</b>\n\n"
            f"🎧 <b>Nomi:</b> <i>{media_info.title}</i>\n"
            f"👤 <b>Ijrochi:</b> {media_info.uploader}\n"
            f"⚡ <b>Format:</b> MP3 (192 kbps)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Marhamat, musiqadan bahramand bo'ling!</i>"
        )

        audio_file = FSInputFile(audio_path)
        keyboard = get_audio_inline_keyboard(media_info.url)

        # Audioni yuborish
        await callback.message.answer_audio(
            audio=audio_file,
            title=media_info.title[:64],
            performer=media_info.uploader[:64],
            duration=media_info.duration,
            caption=audio_caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # Status xabarini tozalash
        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>Musiqani ajratishda xatolik yuz berdi.</b>\n\n"
            f"<i>Xatolik: {e}</i>",
            parse_mode="HTML"
        )


@router.callback_query(F.data == "close_msg")
async def cb_close_message(callback: CallbackQuery):
    """Xabarni o'chirish."""
    try:
        await callback.message.delete()
    except Exception:
        await callback.answer("Xabarni o'chirib bo'lmadi.")
