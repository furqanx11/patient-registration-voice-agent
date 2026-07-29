from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.call_log import CallLogCreate, CallLogOut, VapiWebhookPayload
from src.services.call_log import CallLogService
from src.services.patient import PatientService
from src.utils.logging import get_logger
from src.utils.response import envelope

logger = get_logger()


class CallLogController:
    """HTTP-layer controller for call logs and Vapi webhook handling."""

    def __init__(self, db: Session):
        self.service = CallLogService(db)
        self.patient_service = PatientService(db)

    def receive_vapi_webhook(self, payload: VapiWebhookPayload) -> dict:
        create_data = payload.to_call_log_create()
        if not create_data:
            raise HTTPException(status_code=422, detail="Unsupported Vapi webhook payload")

        # Link to an existing patient by caller phone number if no explicit patient_id.
        if create_data.caller_phone_number and not create_data.patient_id:
            patient = self.patient_service.lookup_by_phone(create_data.caller_phone_number)
            if patient:
                create_data.patient_id = patient.patient_id
                logger.info(
                    "Linked call %s to patient %s by phone",
                    create_data.external_call_id,
                    patient.patient_id,
                )

        call_log = self.service.create_or_update(create_data)
        return envelope(data=CallLogOut.model_validate(call_log).model_dump(mode="json"))

    def list_by_patient(self, patient_id: str) -> dict:
        if not self.patient_service.get_patient(patient_id):
            raise HTTPException(status_code=404, detail="Patient not found")
        calls = self.service.list_by_patient(patient_id)
        return envelope(
            data=[CallLogOut.model_validate(c).model_dump(mode="json") for c in calls]
        )
