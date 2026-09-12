from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_video_inline_keyboard(task_id: str, original_url: str) -> InlineKeyboardMarkup:
    """Video yuborilgandan keyin uning ostida chiquvchi zamonaviy tugmalar."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎵 Videodagi musiqani yuklash (MP3)",
                    callback_data=f"audio:{task_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Asl Instagram havolasi",
                    url=original_url
                ),
                InlineKeyboardButton(
                    text="🗑 Yopish",
                    callback_data="close_msg"
                )
            ]
        ]
    )
    return keyboard


def get_audio_inline_keyboard(original_url: str) -> InlineKeyboardMarkup:
    """Musiqa yuborilgandan so'ng chiquvchi tugmalar."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Instagram posti",
                    url=original_url
                ),
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data="close_msg"
                )
            ]
        ]
    )
    return keyboard


def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Boshlang'ich /start xabaridagi zamonaviy interaktiv menyu."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Qanday ishlatiladi?",
                    callback_data="help_usage"
                ),
                InlineKeyboardButton(
                    text="💎 Imkoniyatlar",
                    callback_data="help_features"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Bot 24/7 Holati",
                    callback_data="help_status"
                ),
                InlineKeyboardButton(
                    text="👨‍💻 Aloqa",
                    url="https://t.me/telegram"
                )
            ]
        ]
    )
    return keyboard


def get_back_inline_keyboard() -> InlineKeyboardMarkup:
    """Bosh menyuga qaytish tugmasi."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Asosiy menyuga qaytish",
                    callback_data="back_to_start"
                )
            ]
        ]
    )
    return keyboard
