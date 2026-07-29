from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from src.services.patient import PatientService
from src.utils.response import envelope


class PatientController:
    """HTTP-layer controller for patient resources."""

    def __init__(self, db: Session):
        self.service = PatientService(db)

    def list(
        self,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        phone_number: str | None = None,
    ) -> dict:
        patients = self.service.list_patients(last_name, date_of_birth, phone_number)
        return envelope(
            data=[PatientOut.model_validate(p).model_dump(mode="json") for p in patients]
        )

    def get(self, patient_id: str) -> dict:
        patient = self.service.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return envelope(data=PatientOut.model_validate(patient).model_dump(mode="json"))

    def create(self, payload: PatientCreate) -> dict:
        patient = self.service.create_patient(payload)
        return envelope(data=PatientOut.model_validate(patient).model_dump(mode="json"))

    def update(self, patient_id: str, payload: PatientUpdate) -> dict:
        patient = self.service.update_patient(patient_id, payload)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return envelope(data=PatientOut.model_validate(patient).model_dump(mode="json"))

    def delete(self, patient_id: str) -> dict:
        patient = self.service.delete_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return envelope(data={"patient_id": patient_id, "deleted": True})
