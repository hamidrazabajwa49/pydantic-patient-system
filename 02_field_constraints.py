"""
02 - Field Constraints

`Field()` (usually combined with `Annotated`) lets you attach *rules* and
*metadata* to a model attribute beyond its bare type: bounds, string length,
default values, titles/descriptions for documentation, and more.

Also introduced here:
    - `EmailStr`  -> validates the string looks like a real email address
    - `AnyUrl`    -> validates the string is a well-formed URL
    - `Optional`  -> the field may be omitted / may be None
    - `strict=True` on a Field -> disables type coercion for that field
      (e.g. an int will NOT be silently accepted for a strict float)

Requires the optional `email-validator` package for `EmailStr`:
    pip install pydantic[email]
"""

from typing import Annotated, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field, ValidationError


class Patient(BaseModel):
    """A patient record with realistic field-level constraints."""

    name: Annotated[
        str,
        Field(
            max_length=50,
            title="Patient name",
            description="Full name of the patient (max 50 characters).",
        ),
    ]
    age: int = Field(gt=5, lt=50, description="Age must be between 5 and 50.")
    # strict=True means "18" (a string) will be rejected instead of coerced.
    weight: Annotated[float, Field(gt=0, strict=True, description="Weight in kg.")]
    married: Annotated[
        bool,
        Field(default=False, title="Marital status", description="Is the patient married?"),
    ]
    allergies: Optional[List[str]] = Field(
        default=None, max_length=5, description="Up to 5 known allergies."
    )
    email: EmailStr
    website: Optional[AnyUrl] = Field(default=None, description="Personal or hospital website.")
    contact_details: Dict[str, str] = Field(
        description="Free-form contact info, e.g. {'phone': '...', 'email': '...'}."
    )


def insert_patient_data(patient: Patient) -> None:
    """Simulate writing a new patient record to a database."""
    print(f"Allergies: {patient.allergies}")
    print("Inserted.\n")


def update_patient_data(patient: Patient) -> None:
    """Simulate updating an existing patient record."""
    print("Updated.\n")


if __name__ == "__main__":
    patient_info = {
        "name": "Ali",
        "age": 30,
        "weight": 65.5,
        "email": "abc@gmail.com",
        "website": "https://example-hospital.com",
        "contact_details": {"phone": "0123456789"},
        "allergies": ["Dust", "Smoke"],
    }

    patient1 = Patient(**patient_info)
    insert_patient_data(patient1)

    # Demonstrate `strict=True`: passing a string where a float is required
    # now fails instead of being silently coerced.
    try:
        Patient(**{**patient_info, "weight": "65.5"})
    except ValidationError as error:
        print("Strict weight field rejected a string as expected:")
        print(error)
