"""
03 - Field Validators

`@field_validator` lets you attach custom validation/transformation logic
to a *single* field, running after Pydantic's own type validation. Two
common uses are shown here:

    1. Rejecting values that pass type-checking but fail a business rule
       (e.g. an email whose domain isn't on an approved list).
    2. Transforming a value on the way in (e.g. normalizing a name to
       uppercase before it's stored on the model).
"""

from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator

# In a real app this would likely come from configuration/a database.
APPROVED_EMAIL_DOMAINS = ["ubl.com", "nbp.com"]


class Patient(BaseModel):
    """A patient record with custom field-level validation rules."""

    name: Annotated[
        str,
        Field(
            max_length=50,
            title="Patient name",
            description="Full name of the patient (max 50 characters).",
        ),
    ]
    age: int = Field(gt=5, lt=50)
    weight: Annotated[float, Field(gt=0, strict=True)]
    married: Annotated[bool, Field(default=False)]
    allergies: Optional[List[str]] = Field(default=None, max_length=5)
    email: EmailStr
    contact_details: Dict[str, str]

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, value: str) -> str:
        """Only allow emails from a pre-approved list of domains."""
        domain = value.split("@")[-1]
        if domain not in APPROVED_EMAIL_DOMAINS:
            raise ValueError(
                f"Email domain '{domain}' is not approved. "
                f"Allowed domains: {APPROVED_EMAIL_DOMAINS}"
            )
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Store every patient name in uppercase for consistency."""
        return value.upper()


def insert_patient_data(patient: Patient) -> None:
    """Simulate writing a new patient record to a database."""
    print(f"Stored name: {patient.name}")
    print("Inserted.\n")


def update_patient_data(patient: Patient) -> None:
    """Simulate updating an existing patient record."""
    print("Updated.\n")


if __name__ == "__main__":
    patient_info = {
        "name": "Ali",
        "age": 30,
        "weight": 65.5,
        "married": True,
        "email": "abc@ubl.com",
        "contact_details": {"phone": "0123456789"},
        "allergies": ["Dust", "Smoke"],
    }

    patient1 = Patient(**patient_info)
    insert_patient_data(patient1)  # name is now "ALI"

    # An email from a domain that isn't approved is rejected.
    try:
        Patient(**{**patient_info, "email": "abc@gmail.com"})
    except ValidationError as error:
        print("Unapproved email domain rejected as expected:")
        print(error)
