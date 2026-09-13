"""
06 - Nested Models

Real-world data is rarely flat. A patient has an address (itself made of
several fields) and potentially several emergency contacts. Pydantic
models can be nested inside one another, and Pydantic will recursively
validate every level -- a nested model gets the same guarantees as a
top-level one.

Concepts covered:
    - Using one `BaseModel` as the type of a field on another
    - A `List[SomeModel]` for a variable-length collection of nested
      records (e.g. multiple emergency contacts)
    - Validation errors correctly point to the exact nested field that
      failed (e.g. `address.postal_code`)
"""

from typing import Annotated, List, Optional

from pydantic import BaseModel, EmailStr, Field, ValidationError


class Address(BaseModel):
    """A postal address, reused as a nested model."""

    street: str
    city: str
    country: str
    postal_code: Annotated[str, Field(max_length=10)]


class EmergencyContact(BaseModel):
    """A single emergency contact for a patient."""

    name: str
    relationship: str
    phone: Annotated[str, Field(min_length=7, max_length=15)]


class Patient(BaseModel):
    """A patient record composed of nested sub-models."""

    name: Annotated[str, Field(max_length=50)]
    age: int = Field(gt=0, lt=120)
    email: EmailStr
    address: Address
    # A patient can list zero or more emergency contacts.
    emergency_contacts: Optional[List[EmergencyContact]] = Field(default=None)


def insert_patient_data(patient: Patient) -> None:
    """Simulate writing a new patient record (with nested data) to a database."""
    print(f"{patient.name} lives in {patient.address.city}, {patient.address.country}")
    if patient.emergency_contacts:
        for contact in patient.emergency_contacts:
            print(f"  Emergency contact: {contact.name} ({contact.relationship})")
    print("Inserted.\n")


if __name__ == "__main__":
    patient_info = {
        "name": "Ali",
        "age": 30,
        "email": "ali@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Lahore",
            "country": "Pakistan",
            "postal_code": "54000",
        },
        "emergency_contacts": [
            {"name": "Sara", "relationship": "Spouse", "phone": "03001234567"},
            {"name": "Bilal", "relationship": "Brother", "phone": "03007654321"},
        ],
    }

    patient1 = Patient(**patient_info)
    insert_patient_data(patient1)

    # A validation error inside a nested model is reported with a clear
    # "path" to the offending field, e.g. `address.postal_code`.
    bad_info = dict(patient_info)
    bad_info["address"] = {**patient_info["address"], "postal_code": "way-too-long-for-a-code"}

    try:
        Patient(**bad_info)
    except ValidationError as error:
        print("Invalid nested address rejected as expected:")
        print(error)

    # Nested models also support `.model_dump()`, producing plain nested
    # dictionaries -- useful for serializing the whole object graph at once.
    print("\nFull nested dump:")
    print(patient1.model_dump())
