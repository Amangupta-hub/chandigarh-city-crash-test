import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ai_status_endpoint():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "gemini_available" in data
    assert "model" in data
    assert "message" in data


def test_ai_analyze_endpoint():
    sample_risk_result = {
        "status": "completed",
        "composite_city_risk_score": 72.5,
        "critical_sectors_count": 3,
        "vulnerable_sectors_count": 5,
        "sector_scores": {
            "SEC-17": {"risk_score": 85.0, "risk_category": "Critical"},
            "SEC-22": {"risk_score": 75.0, "risk_category": "Vulnerable"},
        },
    }
    response = client.post("/api/ai/analyze", json={"risk_result": sample_risk_result})
    assert response.status_code == 200
    data = response.json()
    assert "narrative" in data
    assert len(data["narrative"]) > 0


def test_ai_chat_endpoint():
    response = client.post(
        "/api/ai/chat",
        json={"question": "What happens if power fails in Sector 17?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0


def test_ai_complaint_endpoint():
    response = client.post(
        "/api/ai/complaint",
        json={"text": "Severe water logging in Sector 17 near the main market."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert "severity" in data
