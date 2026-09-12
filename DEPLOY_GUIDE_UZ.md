# 🚀 Instagram Video & Audio Saver Bot: 24/7 Bepul Ishlatish Qo'llanmasi

Ushbu qo'llanmada botingizni qanday qilib noutbukingiz o'chiq holatda ham **24/7 bepul serverda** uzluksiz ishlaydigan qilish ko'rsatilgan.

---

## 1-Qadam: Telegram Bot Tokenini Olish

1. Telegramda [@BotFather](https://t.me/BotFather) botini oching va `/start` bosing.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom bering (masalan: `Mening Instagram Yuklovchim`).
4. Botingizga username bering (oxiri `bot` bilan tugashi shart, masalan: `instasave_uz_bot`).
5. BotFather sizga quyidagicha ko'rinishdagi **HTTP API Token** beradi:
   `7123456789:AAFxxx_xxxxxx_xxxxxxxxx`
6. Ushbu tokenni nusxalab oling.

---

## 2-Qadam: Lokal Kompyuteringizda Sinab Ko'rish

1. Papkadagi `.env` faylini oching (bloknot yoki VS Code orqali).
2. Tokeningizni qo'ying:
   ```env
   BOT_TOKEN=7123456789:AAFxxx_xxxxxx_xxxxxxxxx
   ```
3. Terminalda (PowerShell yoki CMD) quyidagi buyruqni bering:
   ```bash
   python main.py
   ```
4. Telegramda o'z botingizga kiring, `/start` bosing va Instagram'dan istalgan video havolasini yuboring.
5. Video kelgach, pastidagi **«🎵 Videodagi musiqani yuklash (MP3)»** tugmasini bosib musiqasini ham tekshirib ko'ring!

---

## 3-Qadam: Noutbuk O'chiq Bo'lsa Ham 24/7 Ishlatish (Render.com Bepul)

Botingiz kompyuteringiz o'chirilganda ham kechayu-kunduz to'xtovsiz ishlashi uchun uni bepul **Render.com** bulutiga joylaymiz.

### A) Loyihani GitHub'ga yuklash:
1. [GitHub.com](https://github.com) ga kiring va yangi bo'sh repozitoriy yarating (masalan: `instagram-saver-bot`).
2. Loyiha papkasida terminalni ochib, quyidagi buyruqlarni ketma-ket yozing:
   ```bash
   git init
   git add .
   git commit -m "Instagram bot tayyor"
   git branch -M main
   git remote add origin https://github.com/SIZNING_USERNAME/instagram-saver-bot.git
   git push -u origin main
   ```

### B) Render.com da 24/7 Ishga Tushirish:
1. [Render.com](https://render.com) saytiga kiring va GitHub orqali bepul ro'yxatdan o'ting.
2. Yuqori o'ng burchakdagi **«New +»** tugmasini bosing va **«Background Worker»** ni tanlang.
3. Yangi yaratgan GitHub repozitoriyangizni (`instagram-saver-bot`) tanlang.
4. Quyidagi sozlamalarni kiriting:
   - **Name:** `instagram-bot`
   - **Region:** `Frankfurt` (yoki istalgan boshqasi)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Plan:** `Free` (Bepul)
5. **Environment Variables** (Muhit o'zgaruvchilari) bo'limiga tushing va yangi kalit qo'shing:
   - **Key:** `BOT_TOKEN`
   - **Value:** `@BotFather` dan olgan tokeningiz.
6. **«Create Background Worker»** tugmasini bosing!

> [!TIP]
> Bir necha daqiqada Render botingizni o'rnatadi va konsolda `Bot muvaffaqiyatli ishga tushdi` xabari paydo bo'ladi.
> **Tabriklaymiz!** Endi siz noutbukingizni bemalol o'chirib qo'yishingiz mumkin, bot 24/7 rejimida Telegramda uzluksiz xizmat ko'rsatadi!

---

## 4-Qadam: Muqobil Variant (Railway.app orqali)

Agar Render o'rniga Railway afzal bo'lsa:
1. [Railway.app](https://railway.app) ga kiring.
2. **«New Project»** ➔ **«Deploy from GitHub repo»** ni tanlang.
3. **Variables** bo'limida `BOT_TOKEN` ni kiriting.
4. Railway avtomatik ravishda `Procfile` va `Dockerfile` orqali botni 24/7 ishga tushiradi.
