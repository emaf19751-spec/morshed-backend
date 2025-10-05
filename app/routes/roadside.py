from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from app.utils.gpt_helper import ask_gpt

router = APIRouter(prefix="/roadside", tags=["roadside"])

# ----------------------------
# Data Models
# ----------------------------
class RoadsideRequest(BaseModel):
    service: str
    vehicle_make: str
    vehicle_model: str
    year: int
    mileage_km: int

# ----------------------------
# POST - Store Request or Fallback
# ----------------------------
@router.post("")
def roadside_request(req: RoadsideRequest):
    """Stores roadside request in DB, falls back to GPT if DB unavailable"""

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        # GPT fallback
        return {
            "status": "gpt-fallback",
            "advice": ask_gpt(f"Give advice for roadside issue: {req.service}")
        }

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS roadside_requests (
                id SERIAL PRIMARY KEY,
                service TEXT,
                vehicle_make TEXT,
                vehicle_model TEXT,
                year INT,
                mileage_km INT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        cur.execute(
            """
            INSERT INTO roadside_requests (service, vehicle_make, vehicle_model, year, mileage_km)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (req.service, req.vehicle_make, req.vehicle_model, req.year, req.mileage_km)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "message": "Roadside request saved to DB"}
    except Exception as e:
        try:
            # GPT Fallback if DB fails
            gpt_reply = ask_gpt(f"Car service request failed: {req.service}. Provide help text.")
            return {"status": "error-db", "message": str(e), "gpt_advice": gpt_reply}
        except:
            raise HTTPException(status_code=500, detail=f"DB + GPT fallback failed: {e}")





