# main.py
from fastapi import FastAPI, Request
from datetime import datetime
from app.routes import diagnose, roadside
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

# ── NEW: OpenAI client (for GPT-5 fallback) ────────────────────────────────────
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # keep app bootable even if package missing

app = FastAPI(title="Morshed API")

# Allow frontend (Netlify) to call this backend
origins = [
    "https://morshedauto.netlify.app",   # your deployed frontend
    "http://localhost:5173",             # optional: Vite local dev
    "http://127.0.0.1:5500"              # optional: static local dev
]

# Also allow Netlify preview URLs like https://<hash>--morshedauto.netlify.app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.netlify\.app",   # covers preview deploys
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── NEW: initialize and stash OpenAI client/model on app.state ────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # make configurable; default GPT-5

if OpenAI and OPENAI_API_KEY:
    app.state.gpt_client = OpenAI(api_key=OPENAI_API_KEY)
    app.state.gpt_model = OPENAI_MODEL
else:
    # Still let the app run; routers can decide what to do if client missing
    app.state.gpt_client = None
    app.state.gpt_model = None

# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# ----------------------------
# LLM Config Check (no token spend)
# ----------------------------
@app.get("/llm-check")
def llm_check():
    configured = bool(app.state.gpt_client and app.state.gpt_model)
    return {
        "status": "ok" if configured else "not_configured",
        "model": app.state.gpt_model,
        "has_api_key": bool(OPENAI_API_KEY),
    }

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
