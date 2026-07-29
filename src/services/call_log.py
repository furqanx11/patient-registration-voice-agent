from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.call_log import CallLog
from src.repositories.call_log import CallLogRepository
from src.schemas.call_log import CallLogCreate
from src.utils.logging import get_logger

logger = get_logger()


class CallLogService:
    """Business logic for call transcript / call log records."""

    def __init__(self, db: Session):
        self.repo = CallLogRepository(db)

    def create_or_update(self, data: CallLogCreate) -> CallLog:
        existing = None
        if data.external_call_id:
            existing = self.repo.find_by_external_id(data.external_call_id)

        if existing:
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(existing, field, value)
            result = self.repo.update(existing)
            logger.info("Updated call log %s", result.call_id)
            return result

        call_log = CallLog(**data.model_dump())
        result = self.repo.create(call_log)
        logger.info("Created call log %s", result.call_id)
        return result

    def get_call(self, call_id: str) -> Optional[CallLog]:
        return self.repo.get(call_id)

    def list_by_patient(self, patient_id: str) -> List[CallLog]:
        return self.repo.list_by_patient(patient_id)
