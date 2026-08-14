"""
Value Object: Email
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from hr.domain.exceptions.employee_exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email:
    value: str

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise InvalidEmailError("Email cannot be empty")
        normalized = self.value.strip().lower()
        if not self.EMAIL_REGEX.match(normalized):
            raise InvalidEmailError(f"Invalid email format: {self.value}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower()
        return False

    def __hash__(self) -> int:
        return hash(self.value)
