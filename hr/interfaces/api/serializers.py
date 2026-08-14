"""
DRF Serializers — thin request / response shape only.
Business validation lives in the domain layer.
"""
from __future__ import annotations

from rest_framework import serializers


class EmployeeCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    department_id = serializers.UUIDField()
    department_name = serializers.CharField(max_length=150)
    hire_date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=["active", "inactive", "on_leave", "terminated"],
        default="active",
        required=False,
    )


class EmployeeUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    department_id = serializers.UUIDField(required=False)
    department_name = serializers.CharField(max_length=150, required=False)
    hire_date = serializers.DateField(required=False)
    status = serializers.ChoiceField(
        choices=["active", "inactive", "on_leave", "terminated"],
        required=False,
    )
    is_on_leave = serializers.BooleanField(required=False)


class EmployeeResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    department_id = serializers.UUIDField()
    department_name = serializers.CharField()
    hire_date = serializers.DateField()
    status = serializers.CharField()
    is_on_leave = serializers.BooleanField()
    is_deleted = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class PaginatedEmployeesSerializer(serializers.Serializer):
    items = EmployeeResponseSerializer(many=True)
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()


class BulkTransferSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )
    new_department_id = serializers.UUIDField()
    new_department_name = serializers.CharField(max_length=150)


class BulkDeactivateSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )


class DepartmentMetricsSerializer(serializers.Serializer):
    department_id = serializers.UUIDField()
    department_name = serializers.CharField()
    total_employees = serializers.IntegerField()
    employees_on_leave = serializers.IntegerField()
    active_employees = serializers.IntegerField()


class LeaveSummarySerializer(serializers.Serializer):
    total_on_leave = serializers.IntegerField()
    department_id = serializers.UUIDField(allow_null=True, required=False)
