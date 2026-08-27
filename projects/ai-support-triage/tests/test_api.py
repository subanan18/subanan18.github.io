from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_billing_ticket_is_escalated() -> None:
    response = client.post(
        "/triage",
        json={
            "subject": "Payment failed but account charged",
            "message": "I was charged twice and cannot access my account. Please help urgently.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "billing"
    assert body["priority"] == "critical"
    assert body["confidence"] >= 0.8


def test_general_question_uses_safe_fallback() -> None:
    response = client.post(
        "/triage",
        json={"subject": "Opening hours", "message": "What time are you open tomorrow?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "general"
    assert body["priority"] == "low"


def test_batch_triage() -> None:
    response = client.post(
        "/triage/batch",
        json=[
            {"subject": "Login locked", "message": "My account is locked and I cannot access it"},
            {"subject": "API error", "message": "The API keeps returning an error"},
        ],
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
