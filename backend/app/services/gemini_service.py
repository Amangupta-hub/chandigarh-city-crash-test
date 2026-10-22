"""
C3T Gemini AI Service
---------------------
Shared Google Gemini integration for:
  1. Risk analysis narrative — plain-English explanation of stress-test results
  2. Complaint NLP — intelligent extraction from citizen complaint text
  3. AI Chat — context-aware Q&A about Chandigarh city risk data
  4. Vision & Multimodal — photo/image analysis of citizen-reported urban damage
     (waterlogging, potholes, drain blockage, solid waste, fallen trees)
"""

import os
import json
import re
import logging
from typing import Optional, Dict, Any, List

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    genai = None
    HAS_GENAI = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialise Gemini client once at import time
# ---------------------------------------------------------------------------

_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

if HAS_GENAI and _GEMINI_API_KEY:
    try:
        genai.configure(api_key=_GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(
            model_name=_DEFAULT_MODEL,
            generation_config={
                "temperature": 0.4,
                "top_p": 0.9,
                "max_output_tokens": 1024,
            },
        )
        GEMINI_AVAILABLE = True
    except Exception as exc:
        _MODEL = None
        GEMINI_AVAILABLE = False
        logger.warning("Failed to configure Gemini: %s", exc)
else:
    _MODEL = None
    GEMINI_AVAILABLE = False
    logger.warning("GEMINI_API_KEY not set — Gemini features will return stub responses.")


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _get_generative_model(model_name: Optional[str] = None):
    """Return a GenerativeModel instance with fallback."""
    name = model_name or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    return genai.GenerativeModel(
        model_name=name,
        generation_config={
            "temperature": 0.4,
            "top_p": 0.9,
            "max_output_tokens": 1024,
        },
    )


def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response with model fallbacks."""
    if not GEMINI_AVAILABLE or not HAS_GENAI:
        return "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."

    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        "gemini-flash-latest",
        "gemini-3.8-flash",
    ]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = ""
    for name in models_to_try:
        try:
            m = _get_generative_model(name)
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as exc:
            last_error = str(exc)
            if "404" in last_error or "not found" in last_error.lower():
                continue
            break

    logger.error("Gemini API call failed: %s", last_error)
    if "429" in last_error or "quota" in last_error.lower():
        return "⚠️ Gemini API rate limit reached. Please wait a minute before sending another message."
    return f"⚠️ Gemini request failed: {last_error}"


# ---------------------------------------------------------------------------
# 1. Risk Analysis Narrative
# ---------------------------------------------------------------------------

_RISK_SYSTEM_CONTEXT = """
You are C3T-AI, an urban infrastructure risk assistant for Chandigarh, India.
Your role is to help municipal officials understand stress-test results produced
by the C3T (Chandigarh City Crash Test) prototype system.

Important: All scores are illustrative / synthetic demo estimates, not
operational forecasts. Always remind the user of this when summarising scores.

Be concise, action-oriented, and use plain English. Avoid jargon.
Format your response using short paragraphs or bullet points.
"""


def generate_risk_narrative(risk_result: Dict[str, Any]) -> str:
    """
    Given a RiskAssessmentResult dict, generate a plain-English narrative
    with key findings and recommended actions.
    """
    overall = risk_result.get("overall_score", "N/A")
    components = risk_result.get("components", {})
    sectors = risk_result.get("sectors", [])
    cascade = risk_result.get("cascade", [])

    # Build top-3 high-risk sectors string
    sorted_sectors = sorted(sectors, key=lambda s: s.get("score", 0), reverse=True)
    top_sectors_str = "\n".join(
        f"  - {s.get('sector_id', '?')} (score {s.get('score', '?')}, {s.get('category', '?')} risk): {', '.join(s.get('main_factors', []))}"
        for s in sorted_sectors[:5]
    )

    cascade_str = "\n".join(
        f"  - {c.get('from', c.get('from_node', '?'))} → {c.get('to', c.get('to_node', '?'))}: {c.get('description', '')}"
        for c in cascade[:4]
    )

    component_str = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {v}"
        for k, v in components.items()
    )

    prompt = f"""{_RISK_SYSTEM_CONTEXT}

A stress test has just been run on the Chandigarh city model. Here are the results:

OVERALL RISK SCORE: {overall}/100 (synthetic demo index)

COMPONENT SCORES:
{component_str}

TOP SECTORS BY RISK:
{top_sectors_str}

CASCADE LINKS (modeled failure chains):
{cascade_str}

Please provide:
1. A 2-3 sentence executive summary of the situation.
2. The 3 most critical sectors and why they are at risk.
3. 3-4 concrete, prioritised recommended actions for municipal officials.
4. A brief note reminding the user this is a demo/illustrative model.

Keep the total response under 300 words.
"""
    return _call_gemini(prompt)


# ---------------------------------------------------------------------------
# 2. Complaint NLP Extraction (Gemini-powered)
# ---------------------------------------------------------------------------

_COMPLAINT_SYSTEM = """
You are a civic complaint classification assistant for Chandigarh city.
Extract structured information from a citizen complaint message.

You MUST respond with ONLY valid JSON (no markdown, no code blocks).
Use this exact schema:
{
  "category": "<one of: drainage_blockage | surface_waterlogging | waste_hotspot | traffic_disruption | other>",
  "severity": "<one of: low | moderate | high>",
  "sector_id": "<sector-N or null if not mentioned>",
  "location_description": "<brief extracted location or landmark>",
  "confidence": <0.0 to 1.0>,
  "user_must_confirm": true,
  "notes": "<brief explanation of your extraction reasoning>"
}

Rules:
- NEVER guess the sector if it is not mentioned. Set sector_id to null.
- user_must_confirm is ALWAYS true.
- Confidence should reflect how clearly the complaint maps to a category.
"""


def extract_complaint_with_gemini(text: str) -> Dict[str, Any]:
    """
    Use Gemini to intelligently extract structured data from a complaint.
    Falls back to a safe default dict on failure.
    """
    prompt = f"""{_COMPLAINT_SYSTEM}

Complaint text:
\"\"\"{text}\"\"\"

Respond with only the JSON object.
"""
    raw = _call_gemini(prompt)

    # Strip any accidental markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    try:
        data = json.loads(cleaned)
        data["user_must_confirm"] = True  # enforce safety invariant
        return data
    except json.JSONDecodeError:
        logger.warning("Gemini returned non-JSON for complaint extraction: %s", raw)
        return {
            "category": "other",
            "severity": "moderate",
            "sector_id": None,
            "location_description": text.strip(),
            "confidence": 0.3,
            "user_must_confirm": True,
            "notes": f"Gemini response could not be parsed. Raw: {raw[:200]}",
        }


# ---------------------------------------------------------------------------
# 3. Vision & Multimodal Damage Analysis (Gemini-powered)
# ---------------------------------------------------------------------------

_VISION_SYSTEM_PROMPT = """
You are C3T Vision-AI, an expert urban disaster and infrastructure damage analyzer for Chandigarh, India (Digital Public Infrastructure).
Your task is to analyze photos uploaded by citizens or municipal field staff (such as waterlogging, road damage/potholes, clogged stormwater drains, solid waste hotspots, tree falls, or traffic disruptions).

Analyze the visual evidence thoroughly and return a valid JSON object matching this exact schema:
{
  "hazard_type": "<one of: surface_waterlogging | road_damage | drainage_blockage | waste_hotspot | traffic_disruption | tree_fall | other>",
  "category": "<one of: Waterlogging | Road disruption | Drain blockage | Waste hotspot | Other>",
  "severity": "<one of: Low | Moderate | High | Critical>",
  "severity_score": <integer 0 to 100>,
  "confidence": <float 0.0 to 1.0>,
  "sector_id": "<e.g. Sector 17 or null if not identifiable>",
  "location_clues": "<string describing visual landmarks, street signs, building architecture, roundabout or null>",
  "visual_observations": "<detailed description of visible physical conditions, surface defects, materials, standing water, debris>",
  "damage_details": {
    "water_depth_estimate": "<e.g. ankle-deep (2-4 in), knee-deep (12-18 in), tire-submerged, or 'None'>",
    "obstruction_level": "<e.g. partial (~25%), heavy (~60%), complete impassable (100%), or 'None'>",
    "infrastructure_impacted": "<e.g. Stormwater gully grate, bituminous asphalt road surface, sidewalk curbs>"
  },
  "recommended_action": "<concrete immediate action, e.g. Dispatch mobile dewatering pump unit, Deploy asphalt cold-mix repair team, Clear road gully blockage>",
  "action_urgency": "<one of: Standard | High | Immediate>",
  "user_must_confirm": true,
  "summary": "<1-2 sentence concise executive takeaway>"
}

Strict Rules:
- Output ONLY the JSON object. Do NOT wrap in markdown or backticks.
- user_must_confirm MUST always be true.
- If sector cannot be identified from visible signs or landmarks, set sector_id to null. Never hallucinate sector numbers.
- Provide practical, realistic Chandigarh municipal recommendations.
"""


def _simulate_vision_fallback(
    image_bytes: bytes,
    mime_type: str,
    user_notes: Optional[str] = None,
    sector_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """Heuristic fallback when Gemini API key is missing or offline."""
    notes_lower = (user_notes or "").lower()

    if any(k in notes_lower for k in ["pothole", "cracked", "road", "tar", "asphalt", "damage"]):
        hazard = "road_damage"
        category = "Road disruption"
        severity = "High"
        score = 78
        water_depth = "None observed"
        obstruction = "Partial carriageway obstruction (~45%)"
        infra = "Bituminous flexible road pavement wearing course"
        action = "Dispatch Quick-Response Asphalt Patching Unit with cold-mix bitumen"
        obs = "Surface depression with structural cracking, fractured edges, and loose aggregate debris."
    elif any(k in notes_lower for k in ["drain", "clog", "choke", "gully", "grate", "silt"]):
        hazard = "drainage_blockage"
        category = "Drain blockage"
        severity = "High"
        score = 82
        water_depth = "Backwater ponding ~4-6 inches"
        obstruction = "Stormwater gully inlet blocked (~75%)"
        infra = "Road gully chamber and RCC cast-iron grating"
        action = "Dispatch Super-Sucker de-silting machine and gully clearance crew"
        obs = "Stormwater drain gully choked with plastic bags, silt accumulation, and organic matter."
    elif any(k in notes_lower for k in ["garbage", "trash", "waste", "dump", "bin"]):
        hazard = "waste_hotspot"
        category = "Waste hotspot"
        severity = "Moderate"
        score = 64
        water_depth = "None"
        obstruction = "Sidewalk and verge encroachment"
        infra = "Municipal secondary collection bin and berm"
        action = "Reroute compactor truck for priority clearance and sanitization"
        obs = "Uncontrolled municipal solid waste spillage extending onto the pedestrian pathway."
    elif any(k in notes_lower for k in ["tree", "branch", "fallen"]):
        hazard = "tree_fall"
        category = "Road disruption"
        severity = "High"
        score = 74
        water_depth = "None"
        obstruction = "Severe carriageway blockage (~70%)"
        infra = "Arterial road lane, overhead electric line exposure"
        action = "Dispatch Horticulture Department rapid-response chain-saw team"
        obs = "Large fallen tree limb obstructing vehicular transit across arterial carriageway."
    else:
        hazard = "surface_waterlogging"
        category = "Waterlogging"
        severity = "High"
        score = 76
        water_depth = "Approximately 8-14 inches (hubcap level)"
        obstruction = "Severe carriageway submergence (~60% lanes affected)"
        infra = "Road carriageway, stormwater drainage intake, pedestrian curb"
        action = "Deploy tractor-mounted mobile dewatering pump (1000 GPM) to nearest master storm sewer"
        obs = "Extensive surface stormwater pooling spanning across traffic lanes with submerged curb lines."

    sector_id = sector_hint
    if not sector_id:
        sector_match = re.search(r"sector\s*[-_]?\s*(\d+[a-zA-Z]?)", notes_lower)
        if sector_match:
            sector_id = f"Sector {sector_match.group(1).upper()}"

    return {
        "hazard_type": hazard,
        "category": category,
        "severity": severity,
        "severity_score": score,
        "confidence": 0.88 if user_notes else 0.82,
        "sector_id": sector_id,
        "location_clues": "Visible Chandigarh urban streetscape with standard concrete kerbstones" if not sector_id else f"Tagged near {sector_id}",
        "visual_observations": obs,
        "damage_details": {
            "water_depth_estimate": water_depth,
            "obstruction_level": obstruction,
            "infrastructure_impacted": infra,
        },
        "recommended_action": action,
        "action_urgency": "High" if score >= 70 else "Standard",
        "user_must_confirm": True,
        "summary": f"Visual inspection indicates {severity.lower()} {category.lower()} requiring municipal intervention.",
        "gemini_available": False,
        "data_status": "synthetic_demo",
        "score_label": "Unvalidated demo index (0-100)",
    }


def analyze_image_with_gemini(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    user_notes: Optional[str] = None,
    sector_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Multimodal image analysis using Gemini 1.5 Flash.
    Extracts damage severity, water depth, road obstruction, and recommends interventions.
    Falls back gracefully to simulated demo analysis if offline or unconfigured.
    """
    if not GEMINI_AVAILABLE or _MODEL is None:
        return _simulate_vision_fallback(image_bytes, mime_type, user_notes, sector_hint)

    try:
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }
        user_context_parts = []
        if user_notes:
            user_context_parts.append(f"Citizen's notes: \"{user_notes}\"")
        if sector_hint:
            user_context_parts.append(f"Reported sector: \"{sector_hint}\"")
        user_context = ("\n" + "\n".join(user_context_parts)) if user_context_parts else ""

        prompt = f"""{_VISION_SYSTEM_PROMPT}

Analyze this photo of an urban civic issue in Chandigarh.{user_context}

Respond ONLY with the JSON object.
"""
        response = _MODEL.generate_content([image_part, prompt])
        raw = response.text.strip()
        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

        data = json.loads(cleaned)
        data["user_must_confirm"] = True
        data["gemini_available"] = True
        data["data_status"] = "synthetic_demo"
        data["score_label"] = "Unvalidated demo index (0-100)"
        if sector_hint and not data.get("sector_id"):
            data["sector_id"] = sector_hint
        return data

    except Exception as exc:
        logger.warning("Gemini vision analysis failed or non-JSON, falling back: %s", exc)
        fallback = _simulate_vision_fallback(image_bytes, mime_type, user_notes, sector_hint)
        fallback["notes_error"] = str(exc)
        return fallback


# ---------------------------------------------------------------------------
# 4. AI Chat (supports optional visual context)
# ---------------------------------------------------------------------------

_CHAT_SYSTEM = """
You are C3T-AI, an expert assistant for the Chandigarh City Crash Test (C3T)
urban infrastructure risk prototype.

Context about C3T:
- C3T models cascading urban risks across drainage, waterlogging, traffic,
  heat stress, and waste for Chandigarh's sectors.
- All scores are SYNTHETIC DEMO estimates (not real operational data).
- The system covers sectors 1–47 of Chandigarh.
- Risk factors include: rainfall intensity, debris level, drain condition,
  traffic load, temperature.
- Vision & Multimodal analysis can detect waterlogging depth, potholes, and drain blockages.

You help municipal officials, researchers, and hackathon judges understand the
system, interpret results, and explore hypothetical scenarios.

Be helpful, precise, and always remind users when discussing scores that they
are illustrative demo values, not validated forecasts.
"""


def answer_question(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = "image/jpeg",
) -> str:
    """
    Answer a free-form question about C3T, optionally with live context
    (e.g. current stress-test results or sector data) and an optional photo.
    """
    context_block = ""
    if context:
        context_block = f"\n\nCurrent session context (latest stress-test or sector data):\n{json.dumps(context, indent=2)}\n"

    prompt = f"""{_CHAT_SYSTEM}
{context_block}
User question: {question}

Answer concisely (under 200 words). Use bullet points where helpful.
"""
    if image_bytes and GEMINI_AVAILABLE and _MODEL is not None:
        try:
            image_part = {"mime_type": mime_type or "image/jpeg", "data": image_bytes}
            response = _MODEL.generate_content([image_part, prompt])
            return response.text.strip()
        except Exception as exc:
            logger.error("Multimodal chat failed: %s", exc)
            return _call_gemini(prompt)

    return _call_gemini(prompt)
