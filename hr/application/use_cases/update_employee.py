"""
Use Case: UpdateEmployee
"""
from __future__ import annotations

from uuid import UUID

from django.db import transaction

from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.domain.value_objects.employee_status import EmployeeStatus
from hr.domain.exceptions.employee_exceptions import EmployeeNotFoundError
from hr.application.dtos.employee_dtos import EmployeeUpdateDTO, EmployeeResponseDTO


class UpdateEmployeeUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    @transaction.atomic
    def execute(self, employee_id: UUID, dto: EmployeeUpdateDTO) -> EmployeeResponseDTO:
        employee = self._repo.get_by_id(employee_id)
        if employee is None or employee.is_deleted:
            raise EmployeeNotFoundError(str(employee_id))

        status = None
        if dto.status is not None:
            status = EmployeeStatus.from_string(dto.status)

        employee.update(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            department_id=dto.department_id,
            department_name=dto.department_name,
            hire_date=dto.hire_date,
            status=status,
        )

        if dto.is_on_leave is not None:
            employee.set_leave_status(dto.is_on_leave)

        saved = self._repo.save(employee)

        return EmployeeResponseDTO(
            id=saved.id,
            first_name=saved.first_name,
            last_name=saved.last_name,
            full_name=saved.full_name,
            email=str(saved.email),
            department_id=saved.department_id,
            department_name=saved.department_name,
            hire_date=saved.hire_date,
            status=saved.status.value,
            is_on_leave=saved.is_on_leave,
            is_deleted=saved.is_deleted,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
