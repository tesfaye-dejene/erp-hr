"""
Use Cases: Bulk department transfer & bulk deactivate
All inside a single database transaction.
"""
from __future__ import annotations

from uuid import UUID
from typing import List

from django.db import transaction

from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.domain.exceptions.employee_exceptions import EmployeeNotFoundError
from hr.application.dtos.employee_dtos import (
    BulkDepartmentTransferDTO,
    BulkDeactivateDTO,
    EmployeeResponseDTO,
)


class BulkTransferDepartmentUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    @transaction.atomic
    def execute(self, dto: BulkDepartmentTransferDTO) -> List[EmployeeResponseDTO]:
        if not dto.employee_ids:
            return []

        updated = []
        for emp_id in dto.employee_ids:
            employee = self._repo.get_by_id(emp_id)
            if employee is None or employee.is_deleted:
                raise EmployeeNotFoundError(str(emp_id))
            employee.transfer_department(
                new_department_id=dto.new_department_id,
                new_department_name=dto.new_department_name,
            )
            updated.append(employee)

        saved = self._repo.bulk_save(updated)

        return [
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
            for e in saved
        ]


class BulkDeactivateUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    @transaction.atomic
    def execute(self, dto: BulkDeactivateDTO) -> List[EmployeeResponseDTO]:
        if not dto.employee_ids:
            return []

        updated = []
        for emp_id in dto.employee_ids:
            employee = self._repo.get_by_id(emp_id)
            if employee is None or employee.is_deleted:
                raise EmployeeNotFoundError(str(emp_id))
            employee.deactivate()
            updated.append(employee)

        saved = self._repo.bulk_save(updated)

        return [
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
            for e in saved
        ]
