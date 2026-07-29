from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.patient import Patient
from src.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    def __init__(self, db: Session):
        super().__init__(Patient, db)

    def get_active(self, patient_id: str) -> Optional[Patient]:
        return (
            self.db.query(Patient)
            .filter(Patient.patient_id == patient_id, Patient.deleted_at.is_(None))
            .first()
        )

    def list_active(
        self,
        skip: int = 0,
        limit: int = 100,
        last_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> List[Patient]:
        query = self.db.query(Patient).filter(Patient.deleted_at.is_(None))
        if last_name:
            query = query.filter(Patient.last_name.ilike(last_name))
        if date_of_birth:
            query = query.filter(Patient.date_of_birth == date_of_birth)
        if phone_number:
            query = query.filter(Patient.phone_number == phone_number)
        return query.offset(skip).limit(limit).all()

    def find_by_phone(self, phone_number: str) -> Optional[Patient]:
        return (
            self.db.query(Patient)
            .filter(Patient.phone_number == phone_number, Patient.deleted_at.is_(None))
            .first()
        )

    def soft_delete(self, patient: Patient) -> Patient:
        patient.deleted_at = datetime.now(timezone.utc)
        return self.update(patient)
