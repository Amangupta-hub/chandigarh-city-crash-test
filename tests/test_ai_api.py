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


def test_vision_status():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data.get("multimodal_vision_supported") is True
    assert "supported_hazards" in data


def test_vision_analyze_base64_endpoint():
    # 1x1 transparent PNG base64
    tiny_png_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    response = client.post(
        "/api/ai/vision-analyze",
        json={
            "image_base64": tiny_png_b64,
            "mime_type": "image/png",
            "user_notes": "Deep pothole and road cracking on dividing road Sector 22",
            "sector_id": "Sector 22",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "hazard_type" in data
    assert "severity" in data
    assert "severity_score" in data
    assert "visual_observations" in data
    assert "damage_details" in data
    assert "recommended_action" in data
    assert data.get("user_must_confirm") is True
    assert data.get("data_status") == "synthetic_demo"


def test_vision_upload_multipart_endpoint():
    # Simple binary content
    fake_img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    response = client.post(
        "/api/ai/vision-upload",
        files={"file": ("pothole.png", fake_img, "image/png")},
        data={"notes": "Stormwater drain blocked by plastic trash Sector 35", "sector": "Sector 35"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hazard_type"] == "drainage_blockage"
    assert data["category"] == "Drain blockage"
    assert "damage_details" in data


def test_create_report_from_vision_endpoint():
    payload = {
        "confirmed_sector_id": "Sector 17",
        "confirmed_category": "Waterlogging",
        "confirmed_severity": "High",
        "description": "Standing water 1.5 ft high covering two lanes in underpass",
        "confidence": 0.95,
        "media_url": "data:image/png;base64,sample...",
        "recommended_action": "Dispatch tractor dewatering pump unit",
    }
    response = client.post("/api/ai/report-from-vision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sector_id"] == "sector-17"
    assert data["source"] == "vision_ai"
    assert data["status"] == "unverified"
    assert "event_id" in data


def test_ai_multimodal_chat_endpoint():
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    response = client.post(
        "/api/ai/chat",
        json={
            "question": "Does this visible road damage pose a hazard to ambulance routes?",
            "image_base64": tiny_png_b64,
            "mime_type": "image/png",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
