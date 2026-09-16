@echo off
chcp 65001 > nul
title Instagram Video & Music Saver Bot (24/7 Auto-Restart)

:bot_loop
cls
echo =======================================================
echo    Instagram Video & Music Saver Bot ishga tushdi...
echo    (Bot to'xtab qolmasligi uchun avto-qayta ishga tushish yoqilgan)
echo =======================================================
python main.py
echo.
echo [OGOHLANTIRISH] Bot to'xtadi. 5 soniyada avtomatik qayta ishga tushirilmoqda...
timeout /t 5 > nul
goto bot_loop


