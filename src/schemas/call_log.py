from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.utils.phone import normalize_phone


class CallLogBase(BaseModel):
    external_call_id: Optional[str] = None
    patient_id: Optional[str] = None
    caller_phone_number: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None

    @field_validator("caller_phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return normalize_phone(v) if v else v


class CallLogCreate(CallLogBase):
    pass


class CallLogOut(CallLogBase):
    model_config = ConfigDict(from_attributes=True)

    call_id: str
    created_at: datetime
    updated_at: datetime


class VapiCustomer(BaseModel):
    number: Optional[str] = None


class VapiCall(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    transcript: Optional[str] = None
    recordingUrl: Optional[str] = None
    customer: Optional[VapiCustomer] = None


class VapiMessage(BaseModel):
    type: Optional[str] = None
    call: Optional[VapiCall] = None


class VapiWebhookPayload(BaseModel):
    message: Optional[VapiMessage] = None

    def to_call_log_create(self) -> Optional[CallLogCreate]:
        """Flatten a Vapi end-of-call webhook into our internal schema."""
        if not self.message or not self.message.call:
            return None
        call = self.message.call
        return CallLogCreate(
            external_call_id=call.id,
            caller_phone_number=call.customer.number if call.customer else None,
            status=call.status,
            started_at=call.startedAt,
            ended_at=call.endedAt,
            transcript=call.transcript,
            recording_url=call.recordingUrl,
        )
