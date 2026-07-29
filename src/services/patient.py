from typing import List, Optional, Set

from sqlalchemy.orm import Session

from src.models.patient import Patient
from src.repositories.patient import PatientRepository
from src.schemas.patient import PatientCreate, PatientUpdate
from src.utils.logging import get_logger
from src.utils.phone import normalize_phone

logger = get_logger()

# Fields that cannot be NULL in the database. During a partial update,
# we must not overwrite them with None just because Vapi sent an empty string.
REQUIRED_DB_FIELDS: Set[str] = {
    "first_name",
    "last_name",
    "date_of_birth",
    "sex",
    "phone_number",
    "address_line_1",
    "city",
    "state",
    "zip_code",
    "preferred_language",
}


class PatientService:
    """Business logic for patient records."""

    def __init__(self, db: Session):
        self.repo = PatientRepository(db)

    def list_patients(
        self,
        last_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        phone_number: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Patient]:
        return self.repo.list_active(
            skip=skip,
            limit=limit,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=normalize_phone(phone_number),
        )

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        return self.repo.get_active(patient_id)

    def create_patient(self, data: PatientCreate) -> Patient:
        patient = Patient(**data.model_dump())
        result = self.repo.create(patient)
        logger.info(
            "Created patient %s %s (id=%s)",
            result.first_name,
            result.last_name,
            result.patient_id,
        )
        return result

    def update_patient(self, patient_id: str, data: PatientUpdate) -> Optional[Patient]:
        patient = self.repo.get_active(patient_id)
        if not patient:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            # Skip None values for required DB fields to avoid NOT NULL errors.
            # Vapi sends empty strings for unchanged fields, which the schema
            # converts to None; we should not wipe out existing required data.
            if value is None and field in REQUIRED_DB_FIELDS:
                continue
            setattr(patient, field, value)
        result = self.repo.update(patient)
        logger.info("Updated patient %s", patient_id)
        return result

    def delete_patient(self, patient_id: str) -> Optional[Patient]:
        patient = self.repo.get_active(patient_id)
        if not patient:
            return None
        result = self.repo.soft_delete(patient)
        logger.info("Soft-deleted patient %s", patient_id)
        return result

    def lookup_by_phone(self, phone_number: str) -> Optional[Patient]:
        digits = normalize_phone(phone_number)
        if not digits:
            return None
        return self.repo.find_by_phone(digits)
