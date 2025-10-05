from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from openai import OpenAI

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Models
# ----------------------------
class Vehicle(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None

class DiagnoseIn(BaseModel):
    text: str
    vehicle: Optional[Vehicle] = None

class DiagnoseOut(BaseModel):
    causes: List[str]
    advice: str
    cost_qr_range: str
    safety: Optional[str] = None

# ----------------------------
# Helper – Ask GPT fallback
# ----------------------------
def ask_gpt(prompt: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI car mechanic helping users diagnose vehicle issues."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        reply = response.choices[0].message.content.strip()
        return {
            "causes": [reply],
            "advice": "AI-generated automotive advice.",
            "cost_qr_range": "Inspection required for estimate.",
            "safety": "Consult a qualified technician soon."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT error: {str(e)}")

# ----------------------------
# Diagnose endpoint
# ----------------------------
@router.post("/diagnose", response_model=DiagnoseOut)
def diagnose(body: DiagnoseIn):
    try:
        txt = body.text.lower()
        causes, advice, safety, cost = [], "", None, "QAR 150–350"

        # --- Rule-based ---
        if "brake" in txt or "squeal" in txt:
            causes = ["Worn brake pads", "Glazed rotors"]
            advice = "Inspect pads and rotors; replace if worn."
            safety = "Service soon — braking performance reduced."
            cost = "QAR 300–900"

        elif "overheat" in txt:
            causes = ["Coolant leak", "Thermostat stuck", "Radiator fan issue"]
            advice = "Check coolant level, thermostat, and fan."
            safety = "Stop driving if temperature keeps rising."
            cost = "QAR 250–1200"

        elif "start" in txt or "starting" in txt:
            causes = ["Weak battery", "Starter motor issue", "Ignition fault"]
            advice = "Check battery charge, starter, and ignition."
            safety = "If engine won’t start, seek roadside help."
            cost = "QAR 200–1000"

        else:
            gpt_result = ask_gpt(
                f"Vehicle info: {body.vehicle}. Problem: {body.text}. "
                f"Provide likely causes, repair advice, safety warning, and approximate cost (QAR)."
            )
            return DiagnoseOut(**gpt_result)

        return DiagnoseOut(causes=causes, advice=advice, cost_qr_range=cost, safety=safety)

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
