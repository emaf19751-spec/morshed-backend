from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from app.utils.gpt_helper import ask_gpt

router = APIRouter(prefix="/diagnose", tags=["diagnose"])

# ----------------------------
# Data Models
# ----------------------------
class DiagnoseIn(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[int] = None
    symptoms: str

class DiagnoseOut(BaseModel):
    causes: List[str]
    advice: str
    cost_qr_range: str
    safety: Optional[str] = None
    source: str

# ----------------------------
# Endpoint
# ----------------------------
@router.post("", response_model=DiagnoseOut)
def diagnose(body: DiagnoseIn):
    """Smart car problem diagnosis with GPT fallback"""

    txt = body.symptoms.lower()
    causes, advice, safety, cost = [], "", None, "QAR 150–350"
    local_hit = True

    # --- Local rules (offline logic) ---
    if "brake" in txt or "squeal" in txt:
        causes = ["Worn brake pads", "Glazed rotors"]
        advice = "Inspect pads and rotors; replace if worn."
        safety = "Service soon — reduced braking performance."
        cost = "QAR 300–900"

    elif "overheat" in txt:
        causes = ["Coolant leak", "Thermostat stuck", "Radiator fan issue"]
        advice = "Check coolant level, thermostat, and fan."
        safety = "Stop driving if temperature keeps rising."
        cost = "QAR 250–1200"

    elif "start" in txt or "starting" in txt:
        causes = ["Weak battery", "Starter motor issue", "Ignition fault"]
        advice = "Check battery charge, starter, and ignition system."
        safety = "If engine won't start, seek roadside help."
        cost = "QAR 200–1000"

    else:
        # Fallback to GPT
        local_hit = False

    if local_hit:
        return DiagnoseOut(
            causes=causes,
            advice=advice,
            cost_qr_range=cost,
            safety=safety,
            source="local"
        )

    # --- GPT fallback ---
    try:
        prompt = f"A car shows these symptoms: {body.symptoms}. Explain likely causes, advice, cost estimate in QAR, and safety warning (short JSON)."
        response = ask_gpt(prompt)
        return DiagnoseOut(
            causes=response.get("causes", ["Unknown issue"]),
            advice=response.get("advice", "Consult a mechanic."),
            cost_qr_range=response.get("cost_qr_range", "QAR 200–600"),
            safety=response.get("safety"),
            source="gpt"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT fallback failed: {e}")



