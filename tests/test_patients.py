import pytest

MINIMAL_PATIENT = {
    "first_name": "John",
    "last_name": "Smith",
    "date_of_birth": "1985-03-15",
    "sex": "Male",
    "phone_number": "5551234567",
    "address_line_1": "456 Oak Ave",
    "city": "Dallas",
    "state": "TX",
    "zip_code": "75201",
}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_patient(client):
    response = client.post("/patients", json=MINIMAL_PATIENT)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["first_name"] == "John"
    assert data["last_name"] == "Smith"
    assert data["patient_id"] is not None
    assert data["preferred_language"] == "English"


def test_list_patients(client):
    client.post("/patients", json=MINIMAL_PATIENT)
    response = client.get("/patients")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_get_patient(client):
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    response = client.get(f"/patients/{created['patient_id']}")
    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "John"


def test_get_patient_not_found(client):
    response = client.get("/patients/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"] is not None


def test_update_patient(client):
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    response = client.put(
        f"/patients/{created['patient_id']}",
        json={"last_name": "Smith-Jones", "city": "Houston"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["last_name"] == "Smith-Jones"
    assert data["city"] == "Houston"
    assert data["first_name"] == "John"


def test_update_patient_with_vapi_empty_strings(client):
    """Vapi sends empty strings for unchanged fields. Required fields must not be wiped."""
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    response = client.post(
        "/tools/update-patient",
        json={
            "patient_id": created["patient_id"],
            "first_name": "",
            "last_name": "",
            "date_of_birth": "",
            "sex": "",
            "phone_number": "",
            "address_line_1": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "preferred_language": "",
            "email": "jeremy_elliott@gmail.com",
            "address_line_2": "Block 2",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["first_name"] == "John"  # unchanged
    assert data["last_name"] == "Smith"  # unchanged
    assert data["preferred_language"] == "English"  # unchanged
    assert data["email"] == "jeremy_elliott@gmail.com"
    assert data["address_line_2"] == "Block 2"
    assert data["city"] == "Dallas"  # unchanged


def test_delete_patient(client):
    created = client.post("/patients", json=MINIMAL_PATIENT).json()["data"]
    response = client.delete(f"/patients/{created['patient_id']}")
    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True

    response = client.get(f"/patients/{created['patient_id']}")
    assert response.status_code == 404


def test_lookup_by_phone(client):
    client.post("/patients", json=MINIMAL_PATIENT)
    response = client.post("/tools/lookup-by-phone", json={"phone_number": "5551234567"})
    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "John"


def test_lookup_by_phone_not_found(client):
    response = client.post("/tools/lookup-by-phone", json={"phone_number": "0000000000"})
    assert response.status_code == 200
    assert response.json()["data"] is None


def test_phone_number_normalization(client):
    payload = {**MINIMAL_PATIENT, "phone_number": "(555) 123-4567"}
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    assert response.json()["data"]["phone_number"] == "5551234567"


def test_invalid_date_of_birth(client):
    payload = {**MINIMAL_PATIENT, "date_of_birth": "2099-01-01"}
    response = client.post("/patients", json=payload)
    assert response.status_code == 422
    assert "future" in response.json()["error"].lower()


def test_invalid_state(client):
    payload = {**MINIMAL_PATIENT, "state": "XX"}
    response = client.post("/patients", json=payload)
    assert response.status_code == 422


def test_invalid_zip(client):
    payload = {**MINIMAL_PATIENT, "zip_code": "123"}
    response = client.post("/patients", json=payload)
    assert response.status_code == 422
