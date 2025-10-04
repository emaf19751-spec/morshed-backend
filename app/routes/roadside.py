from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import psycopg2
from app.utils.gpt_helper import ask_gpt   # <-- helper we built earlier

router = APIRouter()

# Define request body
class RoadsideRequest(BaseModel):
    service: str
    vehicle_make: str
    vehicle_model: str
    year: int
    mileage_km: int

# POST: Store a new roadside request + GPT fallback
@router.post("/roadside-request")
def roadside_request(req: RoadsideRequest, request: Request):
    try:
        # Always store in DB
        conn = psycopg2.connect(
            host="db",
            port="5432",
            user="morshed",
            password="morshed123",
            dbname="morsheddb"
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO roadside_requests 
            (service, vehicle_make, vehicle_model, year, mileage_km)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (req.service, req.vehicle_make, req.vehicle_model, req.year, req.mileage_km)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Local quick rules
        msg = None
        service = req.service.lower()
        if "battery" in service:
            msg = "🔋 Battery replacement team dispatched."
        elif "tyre" in service or "tire" in service:
            msg = "🛞 Tyre puncture service dispatched."
        elif "van" in service or "garage" in service:
            msg = "🚐 Mobile garage van on the way."
        elif "tow" in service:
            msg = "🚛 Tow truck has been arranged."

        # If no local rule, ask GPT for guidance
        if not msg:
            prompt = f"""
            Roadside request details:
            Service: {req.service}
            Vehicle: {req.vehicle_make} {req.vehicle_model}, {req.year}, {req.mileage_km} km.

            Suggest appropriate roadside assistance action in Qatar context.
            Keep it short and practical, like a dispatcher update.
            """
            gpt_reply = ask_gpt(
                request,
                role="You are a roadside assistance dispatcher.",
                prompt=prompt
            )
            msg = gpt_reply or "✅ Roadside request stored. Assistance will contact you shortly."

        return {"status": "ok", "message": msg}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

# GET: Retrieve all roadside requests
@router.get("/roadside-requests")
def get_roadside_requests():
    try:
        conn = psycopg2.connect(
            host="db",
            port="5432",
            user="morshed",
            password="morshed123",
            dbname="morsheddb"
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT id, service, vehicle_make, vehicle_model, year, mileage_km, created_at
            FROM roadside_requests
            ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        requests = []
        for row in rows:
            requests.append({
                "id": row[0],
                "service": row[1],
                "vehicle_make": row[2],
                "vehicle_model": row[3],
                "year": row[4],
                "mileage_km": row[5],
                "created_at": row[6].isoformat()
            })

        return {"status": "ok", "requests": requests}

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})




