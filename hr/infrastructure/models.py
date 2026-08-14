"""
Django ORM model — persistence only.
No business logic lives here.
"""
from __future__ import annotations

import uuid

from django.db import models


class EmployeeModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    department_id = models.UUIDField(db_index=True)
    department_name = models.CharField(max_length=150)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, default="active", db_index=True)
    is_on_leave = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_employee"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["department_id", "is_deleted"]),
            models.Index(fields=["is_on_leave", "is_deleted"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"
