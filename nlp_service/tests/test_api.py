from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze():
    res = client.post("/analyze", json={
        "user_id": "1",
        "text": "I felt tired and avoided work and kept scrolling"
    })

    assert res.status_code == 200
    data = res.json()

    assert data["emotion"] == "low_energy"
    assert "avoidance" in data["behaviors"]
    assert "distraction" in data["behaviors"]
    assert data["state"] == "avoidance"
