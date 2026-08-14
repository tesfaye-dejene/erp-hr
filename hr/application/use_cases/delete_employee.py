"""
Use Case: SoftDeleteEmployee
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.domain.exceptions.employee_exceptions import EmployeeNotFoundError


class SoftDeleteEmployeeUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    @transaction.atomic
    def execute(self, employee_id: UUID) -> None:
        employee = self._repo.get_by_id(employee_id)
        if employee is None or employee.is_deleted:
            raise EmployeeNotFoundError(str(employee_id))

        employee.soft_delete()
        self._repo.save(employee)
