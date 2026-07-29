from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.controllers.call_log import CallLogController
from src.database import get_db
from src.schemas.call_log import VapiWebhookPayload

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/webhook/vapi")
def vapi_webhook(payload: VapiWebhookPayload, db: Session = Depends(get_db)):
    return CallLogController(db).receive_vapi_webhook(payload)


@router.get("/patient/{patient_id}")
def list_patient_calls(patient_id: str, db: Session = Depends(get_db)):
    return CallLogController(db).list_by_patient(patient_id)
