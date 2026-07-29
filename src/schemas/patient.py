import re
import types
import typing
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from src.utils.phone import normalize_phone

US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}

NAME_RE = re.compile(r"^[A-Za-z'\-]{1,50}$")
ZIP_RE = re.compile(r"^\d{5}(-\d{4})?$")


class Sex(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    decline = "Decline to Answer"


def _is_optional_type(annotation) -> bool:
    """Return True if the annotation accepts None as a valid value."""
    origin = typing.get_origin(annotation)
    if origin is typing.Union or origin is types.UnionType:
        return type(None) in typing.get_args(annotation)
    return False


class BasePatientSchema(BaseModel):
    """Shared base that converts empty strings sent by Vapi into None for optional fields."""

    @model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, values):
        # Only run on raw dict input (e.g. from Vapi/JSON). Skip ORM objects.
        if not isinstance(values, dict):
            return values
        for field, value in values.items():
            if value == "":
                field_info = cls.model_fields.get(field)
                if field_info and _is_optional_type(field_info.annotation):
                    values[field] = None
        return values


class PatientBase(BasePatientSchema):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: Optional[EmailStr] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not NAME_RE.match(v):
            raise ValueError(
                "Name must be 1-50 alphabetic characters, hyphens, or apostrophes"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = normalize_phone(v)
        if digits is None:
            raise ValueError("Phone number must be a valid 10-digit U.S. number")
        return digits

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        v = v.upper()
        if v not in US_STATE_ABBREVIATIONS:
            raise ValueError("State must be a valid 2-letter U.S. state abbreviation")
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        if not ZIP_RE.match(v):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format")
        return v

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        if not (1 <= len(v) <= 100):
            raise ValueError("City must be 1-100 characters")
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BasePatientSchema):
    """All fields optional to support partial updates (PUT with partial body)."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[Sex] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not NAME_RE.match(v):
            raise ValueError(
                "Name must be 1-50 alphabetic characters, hyphens, or apostrophes"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = normalize_phone(v)
        if digits is None:
            raise ValueError("Phone number must be a valid 10-digit U.S. number")
        return digits

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper()
        if v not in US_STATE_ABBREVIATIONS:
            raise ValueError("State must be a valid 2-letter U.S. state abbreviation")
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not ZIP_RE.match(v):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format")
        return v

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not (1 <= len(v) <= 100):
            raise ValueError("City must be 1-100 characters")
        return v


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    created_at: datetime
    updated_at: datetime
