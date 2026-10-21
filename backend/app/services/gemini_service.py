"""
C3T Gemini AI Service
---------------------
Shared Google Gemini integration for:
  1. Risk analysis narrative — plain-English explanation of stress-test results
  2. Complaint NLP — intelligent extraction from citizen complaint text
  3. AI Chat — context-aware Q&A about Chandigarh city risk data
"""

import os
import json
import re
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialise Gemini client once at import time
# ---------------------------------------------------------------------------

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if _GEMINI_API_KEY:
    genai.configure(api_key=_GEMINI_API_KEY)
    _MODEL = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.4,
            "top_p": 0.9,
            "max_output_tokens": 1024,
        },
    )
    GEMINI_AVAILABLE = True
else:
    _MODEL = None
    GEMINI_AVAILABLE = False
    logger.warning("GEMINI_API_KEY not set — Gemini features will return stub responses.")


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    if not GEMINI_AVAILABLE or _MODEL is None:
        return "⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."
    try:
        response = _MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        return f"⚠️ Gemini request failed: {exc}"


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
# 3. AI Chat
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

You help municipal officials, researchers, and hackathon judges understand the
system, interpret results, and explore hypothetical scenarios.

Be helpful, precise, and always remind users when discussing scores that they
are illustrative demo values, not validated forecasts.
"""


def answer_question(
    question: str,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Answer a free-form question about C3T, optionally with live context
    (e.g. current stress-test results or sector data).
    """
    context_block = ""
    if context:
        context_block = f"\n\nCurrent session context (latest stress-test or sector data):\n{json.dumps(context, indent=2)}\n"

    prompt = f"""{_CHAT_SYSTEM}
{context_block}
User question: {question}

Answer concisely (under 200 words). Use bullet points where helpful.
"""
    return _call_gemini(prompt)
