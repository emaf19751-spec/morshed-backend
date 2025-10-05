from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from app.routes import diagnose, roadside
import psycopg2
import os

# ----------------------------
# Initialize FastAPI
# ----------------------------
app = FastAPI(title="Morshed Auto Backend")

# ----------------------------
# CORS
# ----------------------------
origins = [
    "https://morshedauto.netlify.app",  # production frontend
    "http://localhost:5173",            # local dev
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Health Check
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# ----------------------------
# DB Connection Check
# ----------------------------
@app.get("/db-check")
def db_check():
    """Checks Render PostgreSQL connection"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"status": "error", "message": "DATABASE_URL not found in environment"}

        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return {"status": "ok", "message": "Connected to PostgreSQL successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------
# Routers
# ----------------------------
app.include_router(diagnose.router)
app.include_router(roadside.router)



