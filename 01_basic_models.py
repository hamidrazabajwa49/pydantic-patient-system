"""
01 - Basic Models

The simplest possible Pydantic model: a plain class with type-annotated
fields. Pydantic validates and (where possible) coerces incoming data to
match those annotations the moment an instance is created.

Concepts covered:
    - Defining a model with `BaseModel`
    - Automatic type coercion (e.g. a numeric string -> int)
    - What happens when data genuinely can't be coerced (`ValidationError`)
"""

from pydantic import BaseModel, ValidationError


class Patient(BaseModel):
    """A minimal patient record with just a name and an age."""

    name: str
    age: int


def insert_patient_data(patient: Patient) -> None:
    """Simulate writing a new patient record to a database."""
    print(f"Name: {patient.name}")
    print(f"Age: {patient.age}")
    print("Inserted.\n")


def update_patient_data(patient: Patient) -> None:
    """Simulate updating an existing patient record."""
    print(f"Name: {patient.name}")
    print(f"Age: {patient.age}")
    print("Updated.\n")


if __name__ == "__main__":
    # A perfectly typed dictionary -> no surprises.
    clean_data = {"name": "Ali", "age": 30}

    # Pydantic will happily *coerce* a numeric string into an int here,
    # since "20" can be unambiguously converted to 20.
    coerced_data = {"name": "Hassan", "age": "20"}

    patient1 = Patient(**clean_data)
    patient2 = Patient(**coerced_data)

    insert_patient_data(patient1)
    insert_patient_data(patient2)

    # Data that truly cannot be coerced raises a ValidationError instead
    # of silently producing garbage or throwing a generic TypeError.
    try:
        Patient(name="Zara", age="not-a-number")
    except ValidationError as error:
        print("Validation failed as expected:")
        print(error)
