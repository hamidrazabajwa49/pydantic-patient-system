"""
04 - Model Validators

`@field_validator` only sees one field at a time. When a rule depends on
*multiple* fields together, use `@model_validator` instead.

Here, a patient over 60 is required to have an emergency contact listed
in `contact_details` -- a rule that can't be expressed on a single field
because it needs both `age` and `contact_details` at once.

`mode='after'` means the validator runs once every individual field has
already been validated and coerced, so `model` below is a fully-built
`Patient` instance.
"""

from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator, model_validator

APPROVED_EMAIL_DOMAINS = ["ubl.com", "nbp.com"]


class Patient(BaseModel):
    """A patient record with a cross-field business rule."""

    name: Annotated[str, Field(max_length=50)]
    age: int = Field(gt=5, lt=100)
    weight: Annotated[float, Field(gt=0, strict=True)]
    married: Annotated[bool, Field(default=False)]
    allergies: Optional[List[str]] = Field(default=None, max_length=5)
    email: EmailStr
    contact_details: Dict[str, str]

    @model_validator(mode="after")
    def require_emergency_contact_for_seniors(self) -> "Patient":
        """Patients over 60 must have an 'emergency' contact on file."""
        if self.age > 60 and "emergency" not in self.contact_details:
            raise ValueError("Emergency contact needed for patients over 60.")
        return self

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, value: str) -> str:
        domain = value.split("@")[-1]
        if domain not in APPROVED_EMAIL_DOMAINS:
            raise ValueError(f"Email domain '{domain}' is not approved.")
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.upper()


def insert_patient_data(patient: Patient) -> None:
    """Simulate writing a new patient record to a database."""
    print("Inserted.\n")


def update_patient_data(patient: Patient) -> None:
    """Simulate updating an existing patient record."""
    print("Updated.\n")


if __name__ == "__main__":
    senior_patient_info = {
        "name": "Ali",
        "age": 70,
        "weight": 65.5,
        "married": True,
        "email": "abc@ubl.com",
        "contact_details": {"phone": "0123456789", "emergency": "123456789"},
        "allergies": ["Dust", "Smoke"],
    }

    patient1 = Patient(**senior_patient_info)
    insert_patient_data(patient1)

    # Remove the emergency contact -> the cross-field rule now fails.
    invalid_info = dict(senior_patient_info)
    invalid_info["contact_details"] = {"phone": "0123456789"}

    try:
        Patient(**invalid_info)
    except ValidationError as error:
        print("Missing emergency contact rejected as expected:")
        print(error)
