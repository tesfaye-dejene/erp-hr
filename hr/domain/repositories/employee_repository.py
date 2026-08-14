"""
Abstract repository port (interface) for Employee.
Domain layer depends only on this abstraction.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from hr.domain.entities.employee import Employee


class EmployeeRepository(ABC):
    """
    Port that the application layer depends on.
    Concrete implementation lives in infrastructure.
    """

    @abstractmethod
    def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Employee]:
        ...

    @abstractmethod
    def list(
        self,
        *,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20,
        include_deleted: bool = False,
    ) -> Tuple[List[Employee], int]:
        """
        Returns (items, total_count).
        """
        ...

    @abstractmethod
    def save(self, employee: Employee) -> Employee:
        ...

    @abstractmethod
    def soft_delete(self, employee_id: UUID) -> None:
        ...

    @abstractmethod
    def bulk_save(self, employees: List[Employee]) -> List[Employee]:
        ...

    @abstractmethod
    def count_on_leave(self, department_id: Optional[UUID] = None) -> int:
        ...

    @abstractmethod
    def count_by_department(self, department_id: UUID) -> int:
        ...
