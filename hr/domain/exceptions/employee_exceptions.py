"""
Domain-specific exceptions for the HR / Employee context.
"""


class EmployeeDomainError(Exception):
    """Base domain exception."""

    def __init__(self, message: str, code: str = "employee_domain_error"):
        self.message = message
        self.code = code
        super().__init__(message)


class InvalidEmailError(EmployeeDomainError):
    def __init__(self, message: str = "Invalid email"):
        super().__init__(message, code="invalid_email")


class InvalidHireDateError(EmployeeDomainError):
    def __init__(self, message: str = "Invalid hire date"):
        super().__init__(message, code="invalid_hire_date")


class InvalidEmployeeDataError(EmployeeDomainError):
    def __init__(self, message: str = "Invalid employee data"):
        super().__init__(message, code="invalid_employee_data")


class EmployeeNotFoundError(EmployeeDomainError):
    def __init__(self, employee_id: str = ""):
        msg = f"Employee not found: {employee_id}" if employee_id else "Employee not found"
        super().__init__(msg, code="employee_not_found")


class EmployeeAlreadyExistsError(EmployeeDomainError):
    def __init__(self, email: str = ""):
        msg = f"Employee with email already exists: {email}" if email else "Employee already exists"
        super().__init__(msg, code="employee_already_exists")


class DepartmentNotFoundError(EmployeeDomainError):
    def __init__(self, department_id: str = ""):
        msg = f"Department not found: {department_id}" if department_id else "Department not found"
        super().__init__(msg, code="department_not_found")
