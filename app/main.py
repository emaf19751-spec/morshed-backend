from fastapi import FastAPI
from datetime import datetime
from app.routes import diagnose, roadside
from fastapi.middleware.cors import CORSMiddleware
import psycopg2   # <-- add this import here
app = FastAPI(title="Morshed API")
# Allow frontend (Netlify) to call this backend
origins = [
    "https://YOUR-SITE.netlify.app",   # replace with your real Netlify domain
    "https://www.YOURCUSTOMDOMAIN.com", # if you added a custom domain
    "http://localhost:5173",            # optional, for local dev
    "http://127.0.0.1:5500"             # optional, for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, etc.
    allow_headers=["*"],   # all headers allowed
)

# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# ----------------------------
# Database Check Endpoint
# ----------------------------
@app.get("/db-check")
def db_check():
    try:
        conn = psycopg2.connect(
            host="db",
            port="5432",
            user="morshed",
            password="morshed123",
            dbname="morsheddb"
        )
        conn.close()
        return {"status": "ok", "message": "Database connected successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------
# Include Other Routers
# ----------------------------
app.include_router(diagnose.router)
app.include_router(roadside.router)

