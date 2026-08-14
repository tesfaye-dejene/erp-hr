"""
Thin ViewSets — only call use cases and serialize results.
No query logic, no business rules.
"""
from __future__ import annotations

from uuid import UUID

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hr.domain.exceptions.employee_exceptions import (
    EmployeeDomainError,
    EmployeeNotFoundError,
    EmployeeAlreadyExistsError,
    InvalidEmailError,
    InvalidHireDateError,
    InvalidEmployeeDataError,
)
from hr.infrastructure.repositories.employee_repository import DjangoEmployeeRepository
from hr.application.use_cases.list_employees import ListEmployeesUseCase
from hr.application.use_cases.create_employee import CreateEmployeeUseCase
from hr.application.use_cases.update_employee import UpdateEmployeeUseCase
from hr.application.use_cases.delete_employee import SoftDeleteEmployeeUseCase
from hr.application.use_cases.bulk_actions import (
    BulkTransferDepartmentUseCase,
    BulkDeactivateUseCase,
)
from hr.application.services.employee_leave_summary_service import (
    EmployeeLeaveSummaryService,
)
from hr.application.dtos.employee_dtos import (
    EmployeeCreateDTO,
    EmployeeUpdateDTO,
    BulkDepartmentTransferDTO,
    BulkDeactivateDTO,
)
from hr.interfaces.api.serializers import (
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeeResponseSerializer,
    PaginatedEmployeesSerializer,
    BulkTransferSerializer,
    BulkDeactivateSerializer,
    DepartmentMetricsSerializer,
    LeaveSummarySerializer,
)
from hr.interfaces.api.permissions import IsHRStaff


def _error_response(exc: Exception, http_status: int = status.HTTP_400_BAD_REQUEST):
    code = getattr(exc, "code", "error")
    message = getattr(exc, "message", str(exc))
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=http_status,
    )


@method_decorator(csrf_exempt, name="dispatch")
class EmployeeViewSet(viewsets.ViewSet):
    """
    Employee Directory CRUD + search/filter + bulk actions.
    """

    permission_classes = [IsHRStaff]
    authentication_classes = []          # Important: disables CSRF check

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._repo = DjangoEmployeeRepository()

    def list(self, request: Request) -> Response:
        search = request.query_params.get("search") or request.query_params.get("name")
        department_id = request.query_params.get("department") or request.query_params.get(
            "department_id"
        )
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        dept_uuid = None
        if department_id:
            try:
                dept_uuid = UUID(department_id)
            except ValueError:
                return _error_response(
                    InvalidEmployeeDataError("Invalid department_id"),
                    status.HTTP_400_BAD_REQUEST,
                )

        use_case = ListEmployeesUseCase(self._repo)
        result = use_case.execute(
            search=search,
            department_id=dept_uuid,
            page=page,
            page_size=page_size,
        )
        serializer = PaginatedEmployeesSerializer(result)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request: Request, pk: str = None) -> Response:
        try:
            emp_id = UUID(pk)
        except (ValueError, TypeError):
            return _error_response(
                InvalidEmployeeDataError("Invalid employee id"),
                status.HTTP_400_BAD_REQUEST,
            )

        employee = self._repo.get_by_id(emp_id)
        if employee is None or employee.is_deleted:
            return _error_response(
                EmployeeNotFoundError(pk), status.HTTP_404_NOT_FOUND
            )

        from hr.application.dtos.employee_dtos import EmployeeResponseDTO

        dto = EmployeeResponseDTO(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            full_name=employee.full_name,
            email=str(employee.email),
            department_id=employee.department_id,
            department_name=employee.department_name,
            hire_date=employee.hire_date,
            status=employee.status.value,
            is_on_leave=employee.is_on_leave,
            is_deleted=employee.is_deleted,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )
        serializer = EmployeeResponseSerializer(dto)
        return Response({"success": True, "data": serializer.data})

    def create(self, request: Request) -> Response:
        serializer = EmployeeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        dto = EmployeeCreateDTO(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            department_id=data["department_id"],
            department_name=data["department_name"],
            hire_date=data["hire_date"],
            status=data.get("status", "active"),
        )

        try:
            use_case = CreateEmployeeUseCase(self._repo)
            result = use_case.execute(dto)
            out = EmployeeResponseSerializer(result)
            return Response(
                {"success": True, "data": out.data, "message": "Employee created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except EmployeeAlreadyExistsError as e:
            return _error_response(e, status.HTTP_409_CONFLICT)
        except (InvalidEmailError, InvalidHireDateError, InvalidEmployeeDataError) as e:
            return _error_response(e, status.HTTP_400_BAD_REQUEST)
        except EmployeeDomainError as e:
            return _error_response(e)

    def update(self, request: Request, pk: str = None) -> Response:
        try:
            emp_id = UUID(pk)
        except (ValueError, TypeError):
            return _error_response(
                InvalidEmployeeDataError("Invalid employee id"),
                status.HTTP_400_BAD_REQUEST,
            )

        serializer = EmployeeUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        dto = EmployeeUpdateDTO(**data)

        try:
            use_case = UpdateEmployeeUseCase(self._repo)
            result = use_case.execute(emp_id, dto)
            out = EmployeeResponseSerializer(result)
            return Response(
                {"success": True, "data": out.data, "message": "Employee updated successfully"},
                status=status.HTTP_200_OK,
            )
        except EmployeeNotFoundError as e:
            return _error_response(e, status.HTTP_404_NOT_FOUND)
        except (InvalidEmailError, InvalidHireDateError, InvalidEmployeeDataError) as e:
            return _error_response(e, status.HTTP_400_BAD_REQUEST)
        except EmployeeDomainError as e:
            return _error_response(e)

    def partial_update(self, request: Request, pk: str = None) -> Response:
        return self.update(request, pk)

    def destroy(self, request: Request, pk: str = None) -> Response:
        try:
            emp_id = UUID(pk)
        except (ValueError, TypeError):
            return _error_response(
                InvalidEmployeeDataError("Invalid employee id"),
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            use_case = SoftDeleteEmployeeUseCase(self._repo)
            use_case.execute(emp_id)
            return Response(
                {"success": True, "message": "Employee soft-deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except EmployeeNotFoundError as e:
            return _error_response(e, status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], url_path="bulk-transfer")
    def bulk_transfer(self, request: Request) -> Response:
        serializer = BulkTransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        dto = BulkDepartmentTransferDTO(
            employee_ids=data["employee_ids"],
            new_department_id=data["new_department_id"],
            new_department_name=data["new_department_name"],
        )

        try:
            use_case = BulkTransferDepartmentUseCase(self._repo)
            results = use_case.execute(dto)
            out = EmployeeResponseSerializer(results, many=True)
            return Response(
                {"success": True, "data": out.data, "message": "Bulk transfer completed"},
                status=status.HTTP_200_OK,
            )
        except EmployeeNotFoundError as e:
            return _error_response(e, status.HTTP_404_NOT_FOUND)
        except EmployeeDomainError as e:
            return _error_response(e)

    @action(detail=False, methods=["post"], url_path="bulk-deactivate")
    def bulk_deactivate(self, request: Request) -> Response:
        serializer = BulkDeactivateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dto = BulkDeactivateDTO(employee_ids=serializer.validated_data["employee_ids"])

        try:
            use_case = BulkDeactivateUseCase(self._repo)
            results = use_case.execute(dto)
            out = EmployeeResponseSerializer(results, many=True)
            return Response(
                {"success": True, "data": out.data, "message": "Bulk deactivate completed"},
                status=status.HTTP_200_OK,
            )
        except EmployeeNotFoundError as e:
            return _error_response(e, status.HTTP_404_NOT_FOUND)
        except EmployeeDomainError as e:
            return _error_response(e)


@method_decorator(csrf_exempt, name="dispatch")
class LeaveSummaryView(APIView):
    """
    Public query endpoint used by the application shell / other modules.
    """

    permission_classes = [IsHRStaff]
    authentication_classes = []          # Important: disables CSRF check

    def get(self, request: Request) -> Response:
        department_id = request.query_params.get("department_id")
        dept_uuid = None
        if department_id:
            try:
                dept_uuid = UUID(department_id)
            except ValueError:
                return _error_response(
                    InvalidEmployeeDataError("Invalid department_id"),
                    status.HTTP_400_BAD_REQUEST,
                )

        service = EmployeeLeaveSummaryService(DjangoEmployeeRepository())
        result = service.get_employees_on_leave_count(department_id=dept_uuid)
        serializer = LeaveSummarySerializer(result)
        return Response({"success": True, "data": serializer.data})


@method_decorator(csrf_exempt, name="dispatch")
class DepartmentMetricsView(APIView):
    """
    Dashboard endpoint — accepts a department filter and returns HR metrics
    by calling the HR application layer (never HR models directly).
    """

    permission_classes = [IsHRStaff]
    authentication_classes = []          # Important: disables CSRF check

    def get(self, request: Request) -> Response:
        department_id = request.query_params.get("department_id")
        department_name = request.query_params.get("department_name", "")

        if not department_id:
            return _error_response(
                InvalidEmployeeDataError("department_id is required"),
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            dept_uuid = UUID(department_id)
        except ValueError:
            return _error_response(
                InvalidEmployeeDataError("Invalid department_id"),
                status.HTTP_400_BAD_REQUEST,
            )

        service = EmployeeLeaveSummaryService(DjangoEmployeeRepository())
        result = service.get_department_metrics(dept_uuid, department_name)
        serializer = DepartmentMetricsSerializer(result)
        return Response({"success": True, "data": serializer.data})