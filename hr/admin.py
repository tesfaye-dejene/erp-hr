from django.contrib import admin
from hr.infrastructure.models import EmployeeModel


@admin.register(EmployeeModel)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "department_name",
        "status",
        "is_on_leave",
        "is_deleted",
        "hire_date",
    )
    list_filter = ("status", "is_on_leave", "is_deleted", "department_name")
    search_fields = ("first_name", "last_name", "email")
    readonly_fields = ("id", "created_at", "updated_at")
