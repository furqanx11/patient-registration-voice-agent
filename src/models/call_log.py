import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base
from src.models.patient import GUID


def _utcnow():
    return datetime.now(timezone.utc)


class CallLog(Base):
    __tablename__ = "call_logs"

    call_id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_call_id = Column(String(255), nullable=True, index=True)
    patient_id = Column(GUID(), ForeignKey("patients.patient_id"), nullable=True)
    caller_phone_number = Column(String(10), nullable=True)
    status = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    recording_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    patient = relationship("Patient", back_populates="calls")
