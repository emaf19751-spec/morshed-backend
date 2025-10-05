from fastapi import FastAPI
from datetime import datetime
from app.routes import diagnose, roadside
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI(title="Morshed API")

origins = [
    "https://morshedauto.netlify.app",
    "http://localhost:5173",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/db-check")
def db_check():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return {"status": "ok", "message": "Connected to Render PostgreSQL successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Routers
app.include_router(diagnose.router)
app.include_router(roadside.router)

