from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.call_log import CallLog
from src.repositories.base import BaseRepository


class CallLogRepository(BaseRepository[CallLog]):
    def __init__(self, db: Session):
        super().__init__(CallLog, db)

    def find_by_external_id(self, external_call_id: str) -> Optional[CallLog]:
        return (
            self.db.query(CallLog)
            .filter(CallLog.external_call_id == external_call_id)
            .first()
        )

    def list_by_patient(self, patient_id: str) -> List[CallLog]:
        return (
            self.db.query(CallLog)
            .filter(CallLog.patient_id == patient_id)
            .order_by(CallLog.created_at.desc())
            .all()
        )
