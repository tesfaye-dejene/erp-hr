"""
Concrete Django ORM implementation of EmployeeRepository.
"""
from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID

from django.db.models import Q

from hr.domain.entities.employee import Employee
from hr.domain.repositories.employee_repository import EmployeeRepository
from hr.infrastructure.models import EmployeeModel
from hr.infrastructure.mappers.employee_mapper import EmployeeMapper


class DjangoEmployeeRepository(EmployeeRepository):
    def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        try:
            model = EmployeeModel.objects.get(id=employee_id)
            return EmployeeMapper.to_domain(model)
        except EmployeeModel.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[Employee]:
        try:
            model = EmployeeModel.objects.get(email__iexact=email.strip().lower())
            return EmployeeMapper.to_domain(model)
        except EmployeeModel.DoesNotExist:
            return None

    def list(
        self,
        *,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
    ) -> Tuple[List[Employee], int]:
        qs = EmployeeModel.objects.all()

        if not include_deleted:
            qs = qs.filter(is_deleted=False)

        if department_id:
            qs = qs.filter(department_id=department_id)

        if search:
            term = search.strip()
            qs = qs.filter(
                Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(email__icontains=term)
            )

        total = qs.count()
        offset = (page - 1) * page_size
        models = qs.order_by("last_name", "first_name")[offset : offset + page_size]

        return [EmployeeMapper.to_domain(m) for m in models], total

    def save(self, employee: Employee) -> Employee:
        try:
            model = EmployeeModel.objects.get(id=employee.id)
        except EmployeeModel.DoesNotExist:
            model = None

        model = EmployeeMapper.to_model(employee, model)
        model.save()
        return EmployeeMapper.to_domain(model)

    def soft_delete(self, employee_id: UUID) -> None:
        EmployeeModel.objects.filter(id=employee_id).update(is_deleted=True, status="inactive")

    def bulk_save(self, employees: List[Employee]) -> List[Employee]:
        saved = []
        for emp in employees:
            saved.append(self.save(emp))
        return saved

    def count_on_leave(self, department_id: Optional[UUID] = None) -> int:
        qs = EmployeeModel.objects.filter(is_on_leave=True, is_deleted=False)
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs.count()

    def count_by_department(self, department_id: UUID) -> int:
        return EmployeeModel.objects.filter(
            department_id=department_id, is_deleted=False
        ).count()
