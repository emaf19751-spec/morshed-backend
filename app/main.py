from fastapi import FastAPI
from datetime import datetime
from app.routes import diagnose, roadside
import psycopg2   # <-- add this import here

app = FastAPI(title="Morshed API")

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

