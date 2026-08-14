"""
Use Case: CreateEmployee
"""
from __future__ import annotations

from django.db import transaction

from hr.domain.entities.employee import Employee
from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.domain.value_objects.employee_status import EmployeeStatus
from hr.domain.exceptions.employee_exceptions import EmployeeAlreadyExistsError
from hr.application.dtos.employee_dtos import EmployeeCreateDTO, EmployeeResponseDTO


class CreateEmployeeUseCase:
    def __init__(self, repository: EmployeeRepository):
        self._repo = repository

    @transaction.atomic
    def execute(self, dto: EmployeeCreateDTO) -> EmployeeResponseDTO:
        existing = self._repo.get_by_email(dto.email)
        if existing and not existing.is_deleted:
            raise EmployeeAlreadyExistsError(dto.email)

        status = EmployeeStatus.from_string(dto.status)

        employee = Employee.create(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            department_id=dto.department_id,
            department_name=dto.department_name,
            hire_date=dto.hire_date,
            status=status,
        )

        saved = self._repo.save(employee)
        # Events are available via saved.pull_events() for an event bus if needed

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
