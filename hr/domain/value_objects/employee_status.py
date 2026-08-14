"""
Value Object / Enum: EmployeeStatus
"""
from enum import Enum


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

    @classmethod
    def from_string(cls, value: str) -> "EmployeeStatus":
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid employee status: {value}")
