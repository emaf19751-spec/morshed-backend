from fastapi import FastAPI
from datetime import datetime
from app.routes import diagnose, roadside
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

# -------------------------------------------------------
# FastAPI App Setup
# -------------------------------------------------------
app = FastAPI(title="Morshed API")

# Allowed frontend origins
origins = [
    "https://morshedauto.netlify.app",  # your Netlify frontend
    "http://localhost:5173",            # Vite dev (optional)
    "http://127.0.0.1:5500"             # local static preview (optional)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # Allow all methods
    allow_headers=["*"],   # Allow all headers
)

# -------------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# -------------------------------------------------------
# Database Connection Check
# -------------------------------------------------------
@app.get("/db-check")
def db_check():
    """Verifies that the backend can connect to Render PostgreSQL."""
    try:
        # Read DATABASE_URL from environment
        DATABASE_URL = os.getenv("DATABASE_URL")

        if not DATABASE_URL:
            return {"status": "error", "message": "DATABASE_URL not set in environment."}

        # Connect and close immediately to test connection
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return {"status": "ok", "message": "Connected to Render PostgreSQL successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------------------------------------------------------
# Routers
# -------------------------------------------------------
app.include_router(diagnose.router)
app.include_router(roadside.router)


