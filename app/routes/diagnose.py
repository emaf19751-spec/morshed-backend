# app/routes/diagnose.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import re, json

router = APIRouter()

# -------------------------
# Input models (backward compatible)
# -------------------------
class Vehicle(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None

class DiagnoseIn(BaseModel):
    # Accept both "text" and legacy "symptoms"
    text: Optional[str] = None
    symptoms: Optional[str] = None

    # Accept vehicle as nested object or flat fields (legacy)
    vehicle: Optional[Vehicle] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[int] = None
    mileage_km: Optional[int] = None

class DiagnoseOut(BaseModel):
    causes: List[str]
    advice: str
    cost_qr_range: str
    safety: Optional[str] = None

# Utility: extract unified text + vehicle
def _normalize(body: DiagnoseIn):
    text = (body.text or body.symptoms or "").strip()
    veh = body.vehicle.dict() if body.vehicle else {
        "make": body.make,
        "model": body.model,
        "year": body.year,
        "mileage_km": body.mileage_km or body.mileage
    }
    # prune Nones
    veh = {k: v for k, v in veh.items() if v not in (None, "", [])}
    return text.lower(), veh

# Negative start patterns only
NEG_START = [
    r"\bwon'?t start\b", r"\bno start\b", r"\bnot starting\b", r"\bno crank\b",
    r"\bclick(?:ing)? sound\b", r"\bjust clicks\b", r"\bcrank(?:s)? but won'?t start\b"
]
OVERHEAT = [r"\boverheat(?:ing)?\b", r"\bengine temp\b", r"\btemperature (?:high|hot)\b"]
BRAKE_NOISE = [r"\bsqueal(?:ing)?\b", r"\bsqueak(?:ing)?\b", r"\bgrind(?:ing)?\b", r"\bbrake\b"]

def _matches_any(patterns, text):
    return any(re.search(p, text, flags=re.I) for p in patterns)

def _gpt_structured(request: Request, veh: dict, raw_text: str):
    # Ask GPT for pure JSON. If OpenAI client is not configured, ask_gpt returns None.
    from app.utils.gpt_helper import ask_gpt
    prompt = f"""
Return ONLY a JSON object with these keys:
- causes: array of 1-4 very short strings
- advice: one concise paragraph
- cost_qr_range: string like "QAR 300–900"
- safety: string or null

Vehicle: {veh or "unknown"}
Symptoms: {raw_text}
Context: Qatar. Be practical and specific. No preamble, no markdown, JSON only.
"""
    reply = ask_gpt(request, role="You are an expert auto mechanic.", prompt=prompt, temperature=0.2, max_tokens=350)
    if not reply:
        return None
    try:
        data = json.loads(reply)
        # Minimal validation
        return DiagnoseOut(
            causes=[str(c) for c in (data.get("causes") or [])][:4] or ["Inspection required"],
            advice=str(data.get("advice") or "Visit a trusted workshop for diagnosis."),
            cost_qr_range=str(data.get("cost_qr_range") or "QAR 150–350"),
            safety=(data.get("safety") or None)
        )
    except Exception:
        # If model returned text, not JSON, wrap it safely
        return DiagnoseOut(
            causes=["AI analysis"],
            advice=reply,
            cost_qr_range="QAR TBD",
            safety=None
        )

@router.post("/diagnose", response_model=DiagnoseOut)
def diagnose(body: DiagnoseIn, request: Request):
    try:
        txt, veh = _normalize(body)
        raw_text = body.text or body.symptoms or ""

        # Default result (if everything fails)
        default = DiagnoseOut(
            causes=["General inspection required"],
            advice="Visit a trusted workshop for diagnosis.",
            cost_qr_range="QAR 150–350",
            safety=None
        )

        # If nothing meaningful in text, try GPT immediately (if available)
        if len(txt) < 4:
            gpt = _gpt_structured(request, veh, raw_text)
            return gpt or default

        # ---------- Local rules with tighter matching + confidence ----------
        causes, advice, safety, cost = [], "", None, None
        needs_fallback = False

        if _matches_any(BRAKE_NOISE, txt):
            causes = ["Worn brake pads", "Glazed/warped rotors"]
            advice = "Inspect pads & rotors; replace worn parts and bed-in properly."
            safety = "Service soon — braking performance may be reduced."
            cost = "QAR 300–900"

        elif _matches_any(OVERHEAT, txt):
            causes = ["Coolant leak", "Thermostat stuck", "Radiator fan issue"]
            advice = "Check coolant level/leaks, thermostat operation, and fan control."
            safety = "Stop driving if temperature rises — risk of engine damage."
            cost = "QAR 250–1200"

        elif _matches_any(NEG_START, txt):
            # Strong 'won't start' pattern
            causes = ["Weak battery", "Starter motor issue", "Ignition system fault"]
            advice = "Load-test the battery, check starter draw and ignition signals."
            safety = "If engine won’t start, seek roadside help."
            cost = "QAR 200–1000"

        elif "start" in txt or "starting" in txt:
            # Ambiguous: mentions 'start' but not failure → let GPT handle
            needs_fallback = True

        else:
            # Unknown → GPT
            needs_fallback = True

        # ---------- GPT fallback if rule is weak/ambiguous or unmatched ----------
        if needs_fallback or not causes:
            gpt = _gpt_structured(request, veh, raw_text)
            if gpt:
                return gpt
            # else: fall back to rule result or default
            if causes:
                return DiagnoseOut(causes=causes, advice=advice, cost_qr_range=cost or "QAR TBD", safety=safety)
            return default

        # Strong rule → return rule result
        return DiagnoseOut(causes=causes, advice=advice, cost_qr_range=cost or "QAR TBD", safety=safety)

    except Exception as e:
        # Always JSON error
        raise HTTPException(status_code=500, detail={"error": str(e)})


