# app/routes/diagnose.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Vehicle info (nested in request)
class Vehicle(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None

# Input model from frontend
class DiagnoseIn(BaseModel):
    text: str
    vehicle: Optional[Vehicle] = None

# Output model
class DiagnoseOut(BaseModel):
    causes: List[str]
    advice: str
    cost_qr_range: str
    safety: Optional[str] = None


@router.post("/diagnose", response_model=DiagnoseOut)
def diagnose(body: DiagnoseIn, request: Request):
    """
    Diagnose car problems using simple rule-based logic first.
    If no match, fall back to GPT-5 through OpenAI API.
    """
    try:
        txt = body.text.lower()
        causes, advice, safety, cost = [], "", None, None

        # --- Local rules ---
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

        elif "start" in txt or "starting" in txt:
            causes = ["Weak battery", "Starter motor issue", "Ignition system fault"]
            advice = "Check battery charge, starter, and ignition."
            safety = "If engine won’t start, seek roadside help."
            cost = "QAR 200–1000"

        # --- If no match, call GPT-5 ---
        if not causes:
            client = request.app.state.gpt_client
            model = request.app.state.gpt_model
            if client and model:
                gpt_prompt = f"""
                A driver reports this problem with their car.
                Vehicle: {body.vehicle.dict() if body.vehicle else "Unknown"}
                Symptoms: {body.text}

                Provide:
                1. Possible causes (list)
                2. Repair advice
                3. Approximate cost range in QAR
                4. Safety note if relevant
                """
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert auto mechanic."},
                        {"role": "user", "content": gpt_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=300
                )
                reply = completion.choices[0].message.content.strip()

                # For now, just return the GPT reply as advice
                causes = ["See GPT-5 analysis"]
                advice = reply
                cost = "Check details"
                safety = None
            else:
                causes = ["General inspection required"]
                advice = "Visit a trusted workshop for diagnosis."
                cost = "QAR 150–350"

        return DiagnoseOut(
            causes=causes,
            advice=advice,
            cost_qr_range=cost or "QAR TBD",
            safety=safety
        )

    except Exception as e:
        # Always return JSON error
        raise HTTPException(status_code=500, detail={"error": str(e)})

