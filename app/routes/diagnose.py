from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Vehicle info (optional, user can skip)
class Vehicle(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None

# Input model
class DiagnoseIn(BaseModel):
    text: str
    vehicle: Vehicle

# Output model
class DiagnoseOut(BaseModel):
    causes: List[str]
    advice: str
    cost_qr_range: str
    safety: Optional[str] = None

# Endpoint: POST /diagnose/
@router.post("/diagnose/", response_model=DiagnoseOut)
def diagnose(body: DiagnoseIn):
    txt = body.text.lower()
    causes, advice, safety, cost = [], "", None, "QAR 150–350"

    if "brake" in txt or "squeal" in txt:
        causes = ["Worn brake pads", "Glazed rotors"]
        advice = "Inspect pads & rotors; replace if worn."
        safety = "Service soon — reduced braking performance."
        cost = "QAR 300–900"

    elif "overheat" in txt:
        causes = ["Coolant leak", "Thermostat stuck", "Radiator fan issue"]
        advice = "Check coolant, thermostat, and fan operation."
        safety = "Stop driving if temperature keeps rising."
        cost = "QAR 250–1200"

    else:
        causes = ["General inspection required"]
        advice = "Visit a trusted workshop for diagnosis."
        cost = "QAR 150–350"

    return DiagnoseOut(
        causes=causes,
        advice=advice,
        cost_qr_range=cost,
        safety=safety
    )
