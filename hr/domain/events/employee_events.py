"""
Domain Events for Employee aggregate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime


@dataclass(frozen=True)
class EmployeeCreated(DomainEvent):
    employee_id: UUID
    email: str
    department_id: UUID


@dataclass(frozen=True)
class EmployeeUpdated(DomainEvent):
    employee_id: UUID


@dataclass(frozen=True)
class EmployeeSoftDeleted(DomainEvent):
    employee_id: UUID


@dataclass(frozen=True)
class EmployeeStatusChanged(DomainEvent):
    employee_id: UUID
    old_status: str
    new_status: str


@dataclass(frozen=True)
class EmployeeDepartmentTransferred(DomainEvent):
    employee_id: UUID
    from_department_id: UUID
    to_department_id: UUID
