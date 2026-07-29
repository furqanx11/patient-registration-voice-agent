from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.patient import Patient
from src.utils.logging import get_logger

logger = get_logger()


def seed_if_empty(db: Session) -> None:
    """Insert a demo patient if the patients table is empty."""
    existing = db.execute(select(Patient)).first()
    if existing:
        return

    seed = Patient(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 5, 14),
        sex="Female",
        phone_number="5551234567",
        email="jane.doe@example.com",
        address_line_1="123 Main St",
        city="Austin",
        state="TX",
        zip_code="78701",
        preferred_language="English",
    )
    db.add(seed)
    db.commit()
    logger.info("Seeded demo patient: Jane Doe")
