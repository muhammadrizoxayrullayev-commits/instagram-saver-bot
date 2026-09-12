import asyncio
import os
import re
import time
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

import yt_dlp
import imageio_ffmpeg

from config import DOWNLOADS_DIR, TEMP_EXPIRE_MINUTES

# FFmpeg dasturining yo'li (imageio-ffmpeg orqali avtomatik aniqlanadi)
try:
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"


@dataclass
class MediaInfo:
    task_id: str
    video_path: Path
    audio_path: Optional[Path]
    title: str
    uploader: str
    duration: int
    url: str
    file_size_bytes: int
    created_at: float


# Kesh xotirasi: task_id -> MediaInfo
DOWNLOAD_CACHE: Dict[str, MediaInfo] = {}

# Instagram havolalarini aniqlash uchun Regex
INSTAGRAM_URL_REGEX = re.compile(
    r"https?://(?:www\.)?(?:instagram\.com|instagr\.am)/(?:p|reel|reels|tv|stories|share)/[^\s]+",
    re.IGNORECASE
)


def extract_instagram_url(text: str) -> Optional[str]:
    """Matn ichidan Instagram havolasini ajratib oladi."""
    if not text:
        return None
    match = INSTAGRAM_URL_REGEX.search(text)
    if match:
        url = match.group(0).rstrip(".,!?)\"'>")
        return url.strip()
    return None


def clean_title(title: str, max_len: int = 120) -> str:
    """Tavsif matnini tozalaydi va juda uzun bo'lsa qisqartiradi."""
    if not title:
        return "Instagram Video"
    # Taglarni va ortiqcha yangi qatorlarni qisqartirish
    lines = [line.strip() for line in title.splitlines() if line.strip()]
    first_line = lines[0] if lines else "Instagram Video"
    if len(first_line) > max_len:
        return first_line[:max_len] + "..."
    return first_line


def _download_video_sync(url: str, task_id: str) -> MediaInfo:
    """Sinxron tarzda yt-dlp orqali Instagram videosini yuklaydi."""
    output_template = str(DOWNLOADS_DIR / f"{task_id}.%(ext)s")
    
    # yt-dlp sozlamalari
    ydl_opts = {
        'format': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': output_template,
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'instagram': {
                'api': ['ios', 'graphql', 'ajax']
            }
        }
    }

    # Agar root papkada cookies.txt mavjud bo'lsa, undan foydalanish
    cookie_file = Path("cookies.txt")
    if cookie_file.exists():
        ydl_opts['cookiefile'] = str(cookie_file)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        if info_dict is None:
            raise ValueError("Instagram ma'lumotlarini yuklab bo'lmadi.")

        # Fayl nomini aniqlash
        filename = ydl.prepare_filename(info_dict)
        video_path = Path(filename)

        # Agar kengaytma o'zgargan bo'lsa (masalan, .mp4 ga aylantirilgan)
        if not video_path.exists():
            for possible_ext in [".mp4", ".mkv", ".webm"]:
                candidate = DOWNLOADS_DIR / f"{task_id}{possible_ext}"
                if candidate.exists():
                    video_path = candidate
                    break

        if not video_path.exists():
            raise FileNotFoundError(f"Yuklangan video fayl topilmadi: {output_template}")

        raw_title = info_dict.get("title") or info_dict.get("description") or "Instagram Video"
        title = clean_title(raw_title)
        uploader = info_dict.get("uploader") or info_dict.get("channel") or "Instagram Foydalanuvchisi"
        duration = int(info_dict.get("duration") or 0)
        file_size = video_path.stat().st_size

        media_info = MediaInfo(
            task_id=task_id,
            video_path=video_path,
            audio_path=None,
            title=title,
            uploader=uploader,
            duration=duration,
            url=url,
            file_size_bytes=file_size,
            created_at=time.time()
        )

        DOWNLOAD_CACHE[task_id] = media_info
        return media_info


async def download_video(url: str, task_id: str) -> MediaInfo:
    """Asinxron o'ram: yt-dlp ni alohida thread'da xavfsiz ishga tushiradi."""
    return await asyncio.to_thread(_download_video_sync, url, task_id)


def _extract_audio_sync(media_info: MediaInfo) -> Path:
    """FFmpeg yordamida videodan ultra-tezlikda MP3 audio ajratib oladi."""
    audio_path = DOWNLOADS_DIR / f"{media_info.task_id}.mp3"
    
    # Agar MP3 allaqachon tayyorlangan bo'lsa
    if audio_path.exists():
        media_info.audio_path = audio_path
        return audio_path

    # Agar video fayl mavjud bo'lsa, undan to'g'ridan-to'g'ri ajratamiz (1 soniya ichida)
    if media_info.video_path and media_info.video_path.exists():
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", str(media_info.video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "192k",
            str(audio_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and audio_path.exists():
            media_info.audio_path = audio_path
            return audio_path

    # Agar video fayl keshdan o'chirilgan bo'lsa, yt-dlp orqali to'g'ridan-to'g'ri audioni yuklaymiz
    ydl_audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(DOWNLOADS_DIR / f"{media_info.task_id}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
        ydl.download([media_info.url])

    if audio_path.exists():
        media_info.audio_path = audio_path
        return audio_path

    raise FileNotFoundError("Musiqani ajratib olishda xatolik yuz berdi.")


async def extract_audio(media_info: MediaInfo) -> Path:
    """Asinxron o'ram: audioni alohida threadda ajratib oladi."""
    return await asyncio.to_thread(_extract_audio_sync, media_info)


async def cleanup_expired_files():
    """Eskirgan vaqtinchalik video va audio fayllarni o'chirib turadi."""
    while True:
        try:
            now = time.time()
            max_age = TEMP_EXPIRE_MINUTES * 60
            expired_keys = []

            for task_id, media in list(DOWNLOAD_CACHE.items()):
                if now - media.created_at > max_age:
                    expired_keys.append(task_id)
                    # Fayllarni diskdan o'chirish
                    if media.video_path and media.video_path.exists():
                        try:
                            media.video_path.unlink()
                        except Exception:
                            pass
                    if media.audio_path and media.audio_path.exists():
                        try:
                            media.audio_path.unlink()
                        except Exception:
                            pass

            for key in expired_keys:
                DOWNLOAD_CACHE.pop(key, None)

            # Shuningdek, downloads papkasidagi qolib ketgan eskirgan fayllarni tozalash
            for file in DOWNLOADS_DIR.iterdir():
                if file.is_file():
                    file_age = now - file.stat().st_mtime
                    if file_age > max_age:
                        try:
                            file.unlink()
                        except Exception:
                            pass

        except Exception as e:
            print(f"[Cleanup Error] {e}")

        # Har 10 daqiqada tekshirib turadi
        await asyncio.sleep(600)
