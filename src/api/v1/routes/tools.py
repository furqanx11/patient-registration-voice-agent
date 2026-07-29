from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.controllers.vapi_tools import VapiToolsController
from src.database import get_db
from src.schemas.patient import PatientUpdate

router = APIRouter(prefix="/tools", tags=["tools"])


class PhoneLookupRequest(BaseModel):
    phone_number: str


class UpdatePatientToolRequest(PatientUpdate):
    patient_id: str


@router.post("/lookup-by-phone")
def tool_lookup_by_phone(payload: PhoneLookupRequest, db: Session = Depends(get_db)):
    return VapiToolsController(db).lookup_by_phone(payload.phone_number)


@router.post("/update-patient")
def tool_update_patient(payload: UpdatePatientToolRequest, db: Session = Depends(get_db)):
    return VapiToolsController(db).update_patient(payload.patient_id, payload)
