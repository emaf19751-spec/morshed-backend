@echo off
echo 🔄 Restarting Morshed Backend + Database...
cd /d C:\Users\Dell\projects\morshed\backend

:: Stop containers and remove orphans
docker compose down --remove-orphans

:: Rebuild and start fresh
docker compose up --build -d

:: Show status
echo.
echo ✅ Containers restarted successfully. Current status:
docker compose ps

echo.
echo Backend running at: http://localhost:8000
echo Swagger Docs:       http://localhost:8000/docs
echo Postgres DB:        localhost:5432 (user: morshed, pass: morshed123, db: morsheddb)

pause
