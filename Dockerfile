FROM python:3.11-slim

# Tizim uchun zaruriy paketlar va ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko'chirish
COPY . .

# downloads papkasini yaratish
RUN mkdir -p downloads

# Botni ishga tushirish
CMD ["python", "main.py"]
