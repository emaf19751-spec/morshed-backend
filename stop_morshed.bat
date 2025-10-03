@echo off
echo 🛑 Stopping Morshed Backend + Database...
cd /d C:\Users\Dell\projects\morshed\backend

:: Stop containers
docker compose down

pause
