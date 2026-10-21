"""
C3T AI Router — /api/ai/*
--------------------------
Endpoints:
  POST /api/ai/analyze   — Generate Gemini narrative from a stress-test result
  POST /api/ai/chat      — Free-form Q&A with C3T-AI
  POST /api/ai/complaint — Gemini-powered complaint extraction
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.app.services.gemini_service import (
    generate_risk_narrative,
    extract_complaint_with_gemini,
    answer_question,
    GEMINI_AVAILABLE,
)

router = APIRouter(prefix="/api/ai", tags=["Gemini AI"])


# ---------------------------------------------------------------------------
# Schema Models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    risk_result: Dict[str, Any] = Field(
        ..., description="A RiskAssessmentResult dict from the stress-test engine"
    )


class AnalyzeResponse(BaseModel):
    narrative: str
    gemini_available: bool


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=800)
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional latest stress-test result or sector data for context"
    )


class ChatResponse(BaseModel):
    answer: str
    gemini_available: bool


class ComplaintRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=1000)


class ComplaintResponse(BaseModel):
    category: str
    severity: str
    sector_id: Optional[str]
    location_description: str
    confidence: float
    user_must_confirm: bool
    notes: str
    gemini_available: bool


class GeminiStatusResponse(BaseModel):
    gemini_available: bool
    model: str
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status", response_model=GeminiStatusResponse)
def gemini_status():
    """Check whether Gemini API is configured and available."""
    return GeminiStatusResponse(
        gemini_available=GEMINI_AVAILABLE,
        model="gemini-1.5-flash" if GEMINI_AVAILABLE else "none",
        message=(
            "Gemini API is active and ready."
            if GEMINI_AVAILABLE
            else "GEMINI_API_KEY is not set. Add it to your .env file."
        ),
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_risk(request: AnalyzeRequest):
    """
    Send a stress-test result to Gemini and get a plain-English narrative
    with key findings and recommended actions.
    """
    try:
        narrative = generate_risk_narrative(request.risk_result)
        return AnalyzeResponse(narrative=narrative, gemini_available=GEMINI_AVAILABLE)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Ask C3T-AI any question about urban risks, sectors, or the C3T system.
    Optionally pass a `context` dict (latest stress-test result) for richer answers.
    """
    try:
        answer = answer_question(request.question, request.context)
        return ChatResponse(answer=answer, gemini_available=GEMINI_AVAILABLE)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/complaint", response_model=ComplaintResponse)
def extract_complaint(request: ComplaintRequest):
    """
    Use Gemini to intelligently extract structured data from a citizen
    complaint text (category, severity, sector, confidence).
    Always returns user_must_confirm=True for safety.
    """
    try:
        data = extract_complaint_with_gemini(request.text)
        return ComplaintResponse(
            **data,
            gemini_available=GEMINI_AVAILABLE,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
