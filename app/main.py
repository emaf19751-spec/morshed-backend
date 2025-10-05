from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from app.routes import diagnose, roadside
import psycopg2
import os

app = FastAPI(title="Morshed Auto API")

# Allow your Netlify frontend + local dev
origins = [
    "https://morshedauto.netlify.app",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# ----------------------------
# Database Connection Test
# ----------------------------
@app.get("/db-check")
def db_check():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        conn.close()
        return {"status": "ok", "message": "Database connected successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------
# Routers
# ----------------------------
app.include_router(diagnose.router)
app.include_router(roadside.router)
