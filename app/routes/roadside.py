from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2, os
from openai import OpenAI

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Model
# ----------------------------
class RoadsideRequest(BaseModel):
    service: str
    vehicle_make: str
    vehicle_model: str
    year: int
    mileage_km: int

# ----------------------------
# Helper – Fallback GPT suggestion
# ----------------------------
def ask_gpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that helps with vehicle roadside issues."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI support unavailable: {str(e)}"

# ----------------------------
# POST: Store roadside request
# ----------------------------
@router.post("/roadside-request")
def roadside_request(req: RoadsideRequest):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO roadside_requests (service, vehicle_make, vehicle_model, year, mileage_km)
            VALUES (%s, %s, %s, %s, %s)
        """, (req.service, req.vehicle_make, req.vehicle_model, req.year, req.mileage_km))
        conn.commit()
        cur.close()
        conn.close()

        # GPT fallback assistance
        ai_tip = ask_gpt(f"Provide quick roadside help instructions for {req.service} on {req.vehicle_make} {req.vehicle_model} ({req.year}).")

        return {"status": "ok", "message": "Request saved.", "ai_tip": ai_tip}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# GET: Retrieve roadside requests
# ----------------------------
@router.get("/roadside-requests")
def get_requests():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT id, service, vehicle_make, vehicle_model, year, mileage_km, created_at
            FROM roadside_requests ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = []
        for r in rows:
            data.append({
                "id": r[0],
                "service": r[1],
                "vehicle_make": r[2],
                "vehicle_model": r[3],
                "year": r[4],
                "mileage_km": r[5],
                "created_at": r[6].isoformat()
            })

        return {"status": "ok", "requests": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
