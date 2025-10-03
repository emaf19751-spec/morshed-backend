from fastapi import APIRouter
from pydantic import BaseModel
import psycopg2

router = APIRouter()

# Define request body
class RoadsideRequest(BaseModel):
    service: str
    vehicle_make: str
    vehicle_model: str
    year: int
    mileage_km: int

# POST: Store a new roadside request
@router.post("/roadside-request")
def roadside_request(req: RoadsideRequest):
    try:
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

        return {"status": "ok", "message": "Roadside request stored in DB"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        cur.execute("SELECT id, service, vehicle_make, vehicle_model, year, mileage_km, created_at FROM roadside_requests ORDER BY created_at DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert to list of dicts
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
        return {"status": "error", "message": str(e)}



