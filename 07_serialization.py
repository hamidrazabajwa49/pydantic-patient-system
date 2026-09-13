"""
07 - Serialization

Once you have a validated model instance, you'll usually need to turn it
back into a dict or JSON string -- to return from an API, write to a
file, or log it. Pydantic gives fine-grained control over exactly what
comes out.

Concepts covered:
    - `.model_dump()`       -> Python dict
    - `.model_dump_json()`  -> JSON string
    - `include` / `exclude` -> only serialize a subset of fields
    - `exclude_unset`       -> only serialize fields the caller actually set
    - `Field(alias=...)`    -> serialize/deserialize under a different key
      (e.g. matching an external API's naming convention)
"""

from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class Patient(BaseModel):
    """A patient record demonstrating serialization options, including aliases."""

    name: Annotated[str, Field(max_length=50)]
    age: int = Field(gt=0, lt=120)
    # `alias` lets external data use "patientEmail" while the Python
    # attribute stays a clean, snake_case `email`.
    email: EmailStr = Field(alias="patientEmail")
    allergies: Optional[List[str]] = Field(default=None)
    contact_details: Dict[str, str]

    # Allows constructing the model from either the field name or its
    # alias, and enables `by_alias=True` on the way out.
    model_config = {"populate_by_name": True}


if __name__ == "__main__":
    patient_info = {
        "name": "Ali",
        "age": 30,
        "patientEmail": "ali@example.com",
        "allergies": ["Dust"],
        "contact_details": {"phone": "0123456789"},
    }

    patient1 = Patient(**patient_info)

    print("Full dict dump:")
    print(patient1.model_dump())

    print("\nFull JSON dump:")
    print(patient1.model_dump_json())

    print("\nOnly `name` and `age`:")
    print(patient1.model_dump(include={"name", "age"}))

    print("\nEverything except `contact_details`:")
    print(patient1.model_dump(exclude={"contact_details"}))

    print("\nSerialized using field aliases (e.g. for an external API):")
    print(patient1.model_dump(by_alias=True))

    print("\nOnly fields the caller explicitly set (no defaults):")
    partial_patient = Patient(
        name="Hassan",
        age=25,
        patientEmail="hassan@example.com",
        contact_details={"phone": "0123456789"},
    )
    print(partial_patient.model_dump(exclude_unset=True))
