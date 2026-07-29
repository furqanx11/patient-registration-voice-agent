from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.patient import PatientUpdate
from src.services.patient import PatientService
from src.utils.response import envelope


class VapiToolsController:
    """Adapters that expose the same patient logic through Vapi-friendly body-based endpoints."""

    def __init__(self, db: Session):
        self.service = PatientService(db)

    def lookup_by_phone(self, phone_number: str) -> dict:
        patient = self.service.lookup_by_phone(phone_number)
        if not patient:
            return envelope(data=None)
        from src.schemas.patient import PatientOut

        return envelope(data=PatientOut.model_validate(patient).model_dump(mode="json"))

    def update_patient(self, patient_id: str, payload: PatientUpdate) -> dict:
        patient = self.service.update_patient(patient_id, payload)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        from src.schemas.patient import PatientOut

        return envelope(data=PatientOut.model_validate(patient).model_dump(mode="json"))
