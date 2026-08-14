"""
Use Case: ListEmployees
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID
from math import ceil

from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.application.dtos.employee_dtos import (
    EmployeeResponseDTO,
    PaginatedEmployeesDTO,
)


class ListEmployeesUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    def execute(
        self,
        *,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedEmployeesDTO:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        employees, total = self._repo.list(
            search=search,
            department_id=department_id,
            page=page,
            page_size=page_size,
            include_deleted=False,
        )

        items = [
            EmployeeResponseDTO(
                id=e.id,
                first_name=e.first_name,
                last_name=e.last_name,
                full_name=e.full_name,
                email=str(e.email),
                department_id=e.department_id,
                department_name=e.department_name,
                hire_date=e.hire_date,
                status=e.status.value,
                is_on_leave=e.is_on_leave,
                is_deleted=e.is_deleted,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in employees
        ]

        total_pages = ceil(total / page_size) if total > 0 else 0

        return PaginatedEmployeesDTO(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
