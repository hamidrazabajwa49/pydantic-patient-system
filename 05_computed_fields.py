"""
05 - Computed Fields

`@computed_field` turns a `@property` into a value that is treated as a
real model field: it shows up when you call `.model_dump()` or
`.model_dump_json()`, even though it isn't part of the constructor input.

Here, `bmi` is *derived* from `weight` and `height` rather than supplied
by the caller -- it's always kept in sync and can never be set to an
inconsistent value directly.
"""

from typing import Annotated, Dict, List, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)

APPROVED_EMAIL_DOMAINS = ["ubl.com", "nbp.com"]


class Patient(BaseModel):
    """A patient record that derives BMI from weight and height."""

    name: Annotated[str, Field(max_length=50)]
    age: int = Field(gt=5, lt=100)
    weight: Annotated[float, Field(gt=0, strict=True, description="Weight in kg.")]
    height: Annotated[float, Field(gt=0, strict=True, description="Height in cm.")]
    married: Annotated[bool, Field(default=False)]
    allergies: Optional[List[str]] = Field(default=None, max_length=5)
    email: EmailStr
    contact_details: Dict[str, str]

    @model_validator(mode="after")
    def require_emergency_contact_for_seniors(self) -> "Patient":
        if self.age > 60 and "emergency" not in self.contact_details:
            raise ValueError("Emergency contact needed for patients over 60.")
        return self

    @computed_field
    @property
    def bmi(self) -> float:
        """Body Mass Index, derived from weight (kg) and height (cm)."""
        height_m = self.height / 100
        return round(self.weight / (height_m**2), 4)

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
    print(f"BMI: {patient.bmi}")
    print("Inserted.\n")


def update_patient_data(patient: Patient) -> None:
    """Simulate updating an existing patient record."""
    print("Updated.\n")


if __name__ == "__main__":
    patient_info = {
        "name": "Ali",
        "age": 70,
        "weight": 65.5,
        "height": 185.5,
        "married": True,
        "email": "abc@ubl.com",
        "contact_details": {"phone": "0123456789", "emergency": "123456789"},
        "allergies": ["Dust", "Smoke"],
    }

    patient1 = Patient(**patient_info)
    insert_patient_data(patient1)

    # `bmi` appears in the dumped output even though it was never passed in.
    print("Dumped model (includes computed `bmi`):")
    print(patient1.model_dump())
