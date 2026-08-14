"""
Mapper: ORM model ↔ Domain entity
"""
from __future__ import annotations

from hr.domain.entities.employee import Employee
from hr.domain.value_objects.email import Email
from hr.domain.value_objects.employee_status import EmployeeStatus
from hr.infrastructure.models import EmployeeModel


class EmployeeMapper:
    @staticmethod
    def to_domain(model: EmployeeModel) -> Employee:
        return Employee(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=Email(model.email),
            department_id=model.department_id,
            department_name=model.department_name,
            hire_date=model.hire_date,
            status=EmployeeStatus.from_string(model.status),
            is_on_leave=model.is_on_leave,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Employee, model: EmployeeModel | None = None) -> EmployeeModel:
        if model is None:
            model = EmployeeModel(id=entity.id)

        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.email = str(entity.email)
        model.department_id = entity.department_id
        model.department_name = entity.department_name
        model.hire_date = entity.hire_date
        model.status = entity.status.value
        model.is_on_leave = entity.is_on_leave
        model.is_deleted = entity.is_deleted
        # created_at / updated_at are managed by Django or set on create
        if entity.created_at:
            model.created_at = entity.created_at
        if entity.updated_at:
            model.updated_at = entity.updated_at
        return model
