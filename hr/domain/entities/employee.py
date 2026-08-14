"""
Domain Entity: Employee
Pure business object — NO Django / DRF imports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from hr.domain.value_objects.email import Email
from hr.domain.value_objects.employee_status import EmployeeStatus
from hr.domain.exceptions.employee_exceptions import (
    InvalidHireDateError,
    InvalidEmployeeDataError,
)
from hr.domain.events.employee_events import (
    EmployeeCreated,
    EmployeeUpdated,
    EmployeeSoftDeleted,
    EmployeeStatusChanged,
    EmployeeDepartmentTransferred,
)


@dataclass
class Employee:
    """
    Aggregate root for the Employee Directory.
    All business invariants live here.
    """

    id: UUID
    first_name: str
    last_name: str
    email: Email
    department_id: UUID
    department_name: str
    hire_date: date
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    is_on_leave: bool = False
    is_deleted: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _events: list = field(default_factory=list, repr=False)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str | Email,
        department_id: UUID,
        department_name: str,
        hire_date: date,
        status: EmployeeStatus = EmployeeStatus.ACTIVE,
    ) -> "Employee":
        cls._validate_name(first_name, "first_name")
        cls._validate_name(last_name, "last_name")
        cls._validate_hire_date(hire_date)

        email_vo = email if isinstance(email, Email) else Email(email)

        employee = cls(
            id=uuid4(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email_vo,
            department_id=department_id,
            department_name=department_name,
            hire_date=hire_date,
            status=status,
            is_on_leave=False,
            is_deleted=False,
        )
        employee._record(
            EmployeeCreated(
                employee_id=employee.id,
                email=str(employee.email),
                department_id=employee.department_id,
                occurred_at=datetime.utcnow(),
            )
        )
        return employee

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------
    def update(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str | Email] = None,
        department_id: Optional[UUID] = None,
        department_name: Optional[str] = None,
        hire_date: Optional[date] = None,
        status: Optional[EmployeeStatus] = None,
    ) -> None:
        if self.is_deleted:
            raise InvalidEmployeeDataError("Cannot update a deleted employee")

        if first_name is not None:
            self._validate_name(first_name, "first_name")
            self.first_name = first_name.strip()

        if last_name is not None:
            self._validate_name(last_name, "last_name")
            self.last_name = last_name.strip()

        if email is not None:
            self.email = email if isinstance(email, Email) else Email(email)

        if hire_date is not None:
            self._validate_hire_date(hire_date)
            self.hire_date = hire_date

        old_department_id = self.department_id
        if department_id is not None and department_id != self.department_id:
            self.department_id = department_id
            if department_name:
                self.department_name = department_name
            self._record(
                EmployeeDepartmentTransferred(
                    employee_id=self.id,
                    from_department_id=old_department_id,
                    to_department_id=self.department_id,
                    occurred_at=datetime.utcnow(),
                )
            )
        elif department_name is not None:
            self.department_name = department_name

        if status is not None and status != self.status:
            old_status = self.status
            self.status = status
            self._record(
                EmployeeStatusChanged(
                    employee_id=self.id,
                    old_status=old_status.value,
                    new_status=status.value,
                    occurred_at=datetime.utcnow(),
                )
            )

        self.updated_at = datetime.utcnow()
        self._record(
            EmployeeUpdated(
                employee_id=self.id,
                occurred_at=datetime.utcnow(),
            )
        )

    def soft_delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self.status = EmployeeStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self._record(
            EmployeeSoftDeleted(
                employee_id=self.id,
                occurred_at=datetime.utcnow(),
            )
        )

    def set_leave_status(self, on_leave: bool) -> None:
        if self.is_on_leave == on_leave:
            return
        old = self.is_on_leave
        self.is_on_leave = on_leave
        self.updated_at = datetime.utcnow()
        self._record(
            EmployeeStatusChanged(
                employee_id=self.id,
                old_status="on_leave" if old else "active",
                new_status="on_leave" if on_leave else "active",
                occurred_at=datetime.utcnow(),
            )
        )

    def transfer_department(self, new_department_id: UUID, new_department_name: str) -> None:
        if self.is_deleted:
            raise InvalidEmployeeDataError("Cannot transfer a deleted employee")
        if new_department_id == self.department_id:
            return
        old = self.department_id
        self.department_id = new_department_id
        self.department_name = new_department_name
        self.updated_at = datetime.utcnow()
        self._record(
            EmployeeDepartmentTransferred(
                employee_id=self.id,
                from_department_id=old,
                to_department_id=new_department_id,
                occurred_at=datetime.utcnow(),
            )
        )

    def deactivate(self) -> None:
        if self.status == EmployeeStatus.INACTIVE:
            return
        old = self.status
        self.status = EmployeeStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self._record(
            EmployeeStatusChanged(
                employee_id=self.id,
                old_status=old.value,
                new_status=EmployeeStatus.INACTIVE.value,
                occurred_at=datetime.utcnow(),
            )
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def pull_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events

    def _record(self, event) -> None:
        self._events.append(event)

    @staticmethod
    def _validate_name(value: str, field_name: str) -> None:
        if not value or not value.strip():
            raise InvalidEmployeeDataError(f"{field_name} cannot be empty")
        if len(value.strip()) < 2:
            raise InvalidEmployeeDataError(f"{field_name} must be at least 2 characters")

    @staticmethod
    def _validate_hire_date(hire_date: date) -> None:
        if hire_date > date.today():
            raise InvalidHireDateError("Hire date cannot be in the future")
        if hire_date.year < 1950:
            raise InvalidHireDateError("Hire date is unreasonably old")
