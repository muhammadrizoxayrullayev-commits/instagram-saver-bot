@echo off
chcp 65001 > nul
title Instagram Video & Music Saver Bot
echo =======================================================
echo    Instagram Video & Music Saver Bot ishga tushirilmoqda...
echo =======================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Xatolik yuz berdi! Iltimos, yuqoridagi xabarni o'qing.
    pause
)
