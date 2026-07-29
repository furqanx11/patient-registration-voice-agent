from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.controllers.patient import PatientController
from src.database import get_db
from src.schemas.patient import PatientCreate, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
def list_patients(
    last_name: Optional[str] = Query(None),
    date_of_birth: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return PatientController(db).list(last_name, date_of_birth, phone_number)


@router.get("/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    return PatientController(db).get(patient_id)


@router.post("", status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    return PatientController(db).create(payload)


@router.put("/{patient_id}")
def update_patient(
    patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db)
):
    return PatientController(db).update(patient_id, payload)


@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    return PatientController(db).delete(patient_id)
