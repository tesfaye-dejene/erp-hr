"""
Application-layer Query Service (public contract for other modules).

Other bounded contexts (Dashboard, application shell, etc.) must use this
service instead of importing HR models or repositories directly.
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.application.dtos.employee_dtos import (
    EmployeeLeaveSummaryDTO,
    DepartmentMetricsDTO,
)


class EmployeeLeaveSummaryService:
    """
    Read-only aggregates exposed to other modules.
    """

    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    def get_employees_on_leave_count(
        self, department_id: Optional[UUID] = None
    ) -> EmployeeLeaveSummaryDTO:
        count = self._repo.count_on_leave(department_id=department_id)
        return EmployeeLeaveSummaryDTO(
            total_on_leave=count,
            department_id=department_id,
        )

    def get_department_metrics(
        self, department_id: UUID, department_name: str = ""
    ) -> DepartmentMetricsDTO:
        total = self._repo.count_by_department(department_id)
        on_leave = self._repo.count_on_leave(department_id=department_id)
        # active ≈ total - on_leave (simplified; real system may track status more precisely)
        active = max(0, total - on_leave)

        return DepartmentMetricsDTO(
            department_id=department_id,
            department_name=department_name,
            total_employees=total,
            employees_on_leave=on_leave,
            active_employees=active,
        )
