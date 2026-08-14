"""
Application DTOs — data structures that cross layer boundaries.
No domain entities or ORM models leak out of the application layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class EmployeeCreateDTO:
    first_name: str
    last_name: str
    email: str
    department_id: UUID
    department_name: str
    hire_date: date
    status: str = "active"


@dataclass
class EmployeeUpdateDTO:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None
    is_on_leave: Optional[bool] = None


@dataclass
class EmployeeResponseDTO:
    id: UUID
    first_name: str
    last_name: str
    full_name: str
    email: str
    department_id: UUID
    department_name: str
    hire_date: date
    status: str
    is_on_leave: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class PaginatedEmployeesDTO:
    items: List[EmployeeResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class BulkDepartmentTransferDTO:
    employee_ids: List[UUID]
    new_department_id: UUID
    new_department_name: str


@dataclass
class BulkDeactivateDTO:
    employee_ids: List[UUID]


@dataclass
class EmployeeLeaveSummaryDTO:
    total_on_leave: int
    department_id: Optional[UUID] = None


@dataclass
class DepartmentMetricsDTO:
    department_id: UUID
    department_name: str
    total_employees: int
    employees_on_leave: int
    active_employees: int
