import pytest

MINIMAL_PATIENT = {
    "first_name": "Alice",
    "last_name": "Wonder",
    "date_of_birth": "1992-08-20",
    "sex": "Female",
    "phone_number": "5559876543",
    "address_line_1": "789 Pine Rd",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
}

VAPI_WEBHOOK = {
    "message": {
        "type": "end-of-call-report",
        "call": {
            "id": "call_abc_123",
            "status": "ended",
            "startedAt": "2024-06-01T10:00:00Z",
            "endedAt": "2024-06-01T10:05:00Z",
            "customer": {"number": "+15559876543"},
            "transcript": "Hi, I'd like to register.",
            "recordingUrl": "https://example.com/recording.mp3",
        },
    }
}


def test_vapi_webhook_creates_call_log(client):
    response = client.post("/calls/webhook/vapi", json=VAPI_WEBHOOK)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["external_call_id"] == "call_abc_123"
    assert data["transcript"] == "Hi, I'd like to register."
    assert data["caller_phone_number"] == "5559876543"
    assert data["call_id"] is not None


def test_vapi_webhook_links_to_patient_by_phone(client):
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    response = client.post("/calls/webhook/vapi", json=VAPI_WEBHOOK)
    assert response.status_code == 200
    assert response.json()["data"]["patient_id"] == created["patient_id"]


def test_list_calls_by_patient(client):
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    client.post("/calls/webhook/vapi", json=VAPI_WEBHOOK)

    response = client.get(f"/calls/patient/{created['patient_id']}")
    assert response.status_code == 200
    calls = response.json()["data"]
    assert len(calls) == 1
    assert calls[0]["external_call_id"] == "call_abc_123"


def test_list_calls_patient_not_found(client):
    response = client.get("/calls/patient/no-such-id")
    assert response.status_code == 404
