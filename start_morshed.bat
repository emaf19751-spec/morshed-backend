@echo off
echo 🚀 Starting Morshed Backend + Database...
cd /d C:\Users\Dell\projects\morshed\backend

:: Start Docker containers in detached mode
docker compose up --build -d

:: Show status
echo.
echo ✅ Current container status:
docker compose ps

echo.
echo Backend running at: http://localhost:8000
echo Swagger Docs:       http://localhost:8000/docs
echo Postgres DB:        localhost:5432 (user: morshed, pass: morshed123, db: morsheddb)

pause
