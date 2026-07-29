import logging

from src.config import Settings


def configure_logging(level: str) -> logging.Logger:
    """Configure the root application logger."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("patient_registration")


def get_logger() -> logging.Logger:
    return logging.getLogger("patient_registration")
