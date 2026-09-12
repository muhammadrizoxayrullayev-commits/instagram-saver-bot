from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards import get_start_inline_keyboard, get_back_inline_keyboard
from config import BOT_VERSION

router = Router()


def get_welcome_text(user_full_name: str) -> str:
    return (
        f"👋 <b>Assalomu alaykum, {user_full_name}!</b>\n\n"
        f"✨ <b>Instagram Media & Music Downloader</b> botiga xush kelibsiz!\n\n"
        f"<blockquote>"
        f"Bu bot orqali siz <b>Instagram</b> tarmog'idagi istalgan <b>Reels</b>, <b>Video</b> "
        f"va <b>Postlar</b>ni eng yuqori sifatda (HD) yuklab olishingiz va "
        f"videodagi audio treklarni alohida <b>MP3</b> formatida olishingiz mumkin."
        f"</blockquote>\n\n"
        f"📥 <b>Foydalanish juda oson:</b>\n"
        f"Shunchaki menga Instagram'dan nusxalangan havolani yuboring!\n\n"
        f"⚡ <i>Quyidagi tugmalar orqali to'liq imkoniyatlar bilan tanishishingiz mumkin:</i>"
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Foydalanuvchi /start yuborganida ko'rsatiladigan zamonaviy xabar."""
    user_name = message.from_user.full_name if message.from_user else "Foydalanuvchi"
    await message.answer(
        text=get_welcome_text(user_name),
        reply_markup=get_start_inline_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Qo'llanma xabari."""
    help_text = (
        "📖 <b>Botdan foydalanish qo'llanmasi:</b>\n\n"
        "1️⃣ Instagram ilovasida yoqqan Reels yoki videoni oching.\n"
        "2️⃣ <b>Ulashish (Share)</b> tugmasini bosib, <b>Havoladan nusxa olish (Copy Link)</b>ni tanlang.\n"
        "3️⃣ Nusxalangan havolani to'g'ridan-to'g'ri ushbu botga yuboring.\n"
        "4️⃣ Bot videoni yuklab beradi. Agar videodagi musiqa kerak bo'lsa, video ostidagi <b>«🎵 Videodagi musiqani yuklash»</b> tugmasini bosing!\n\n"
        "🌐 <i>Bot bulutli serverda 24/7 rejimida uzluksiz ishlaydi.</i>"
    )
    await message.answer(
        text=help_text,
        reply_markup=get_back_inline_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help_usage")
async def cb_help_usage(callback: CallbackQuery):
    """Qanday ishlatiladi bo'limi."""
    usage_text = (
        "🚀 <b>Qanday ishlatiladi?</b>\n\n"
        "🔹 Instagram ilovasini oching.\n"
        "🔹 O'zingizga yoqqan <b>Reels</b>, <b>Post</b> yoki <b>Video</b>ni tanlang.\n"
        "🔹 <b>Ulashish (Share / Samolyotcha belgisi)</b> ➔ <b>Copy Link (Havolani nusxalash)</b>.\n"
        "🔹 Havolani bu yerga tashlang va bir necha soniyada tayyor natijani oling!\n\n"
        "🎶 <b>Musiqa olish:</b> Video kelgach, uning ostidagi tugmani bosish kifoya."
    )
    await callback.message.edit_text(
        text=usage_text,
        reply_markup=get_back_inline_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help_features")
async def cb_help_features(callback: CallbackQuery):
    """Bot imkoniyatlari bo'limi."""
    features_text = (
        "💎 <b>Botning asosiy afzalliklari:</b>\n\n"
        "⚡ <b>Yuqori tezlik:</b> Optimallashtirilgan yuklash mexanizmi.\n"
        "🎬 <b>HD Sifat:</b> Videolar asl sifatda (1080p gacha) yuklanadi.\n"
        "🎵 <b>Tezkor MP3 ajratish:</b> 1 soniyada videodan musiqani chiqarish.\n"
        "☁️ <b>24/7 Ishlash:</b> Noutbuk o'chiq bo'lsa ham serverda doim faol.\n"
        "🛡 <b>Xavfsiz va toza:</b> Reklamalarsiz va ortiqcha spam yo'q."
    )
    await callback.message.edit_text(
        text=features_text,
        reply_markup=get_back_inline_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help_status")
async def cb_help_status(callback: CallbackQuery):
    """24/7 server holati."""
    status_text = (
        "🌐 <b>Server va Bot holati:</b>\n\n"
        "✅ <b>Holati:</b> Faol (Online)\n"
        "⏱ <b>Rejim:</b> 24/7 Uzluksiz\n"
        f"🤖 <b>Versiya:</b> v{BOT_VERSION}\n"
        "⚡ <b>Tezlik:</b> Yuqori (Ultra-Fast)\n\n"
        "<i>Bot bulutli serverda ishlamoqda, har qanday vaqtda havola yuborishingiz mumkin!</i>"
    )
    await callback.message.edit_text(
        text=status_text,
        reply_markup=get_back_inline_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery):
    """Asosiy menyuga qaytish."""
    user_name = callback.from_user.full_name if callback.from_user else "Foydalanuvchi"
    await callback.message.edit_text(
        text=get_welcome_text(user_name),
        reply_markup=get_start_inline_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
