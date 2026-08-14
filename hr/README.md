# HR Module — Employee Directory (DDD / Clean Architecture)

This module implements the **Human Resource (HR) Employee Directory** following the same
Domain-Driven Design + Clean Architecture layering used by the Inventory module.

## Folder Structure

```
hr/
├── domain/                          # Pure business logic (no Django imports)
│   ├── entities/
│   │   └── employee.py              # Aggregate root
│   ├── value_objects/
│   │   ├── email.py
│   │   └── employee_status.py
│   ├── repositories/
│   │   └── employee_repository.py   # Abstract port (interface)
│   ├── exceptions/
│   │   └── employee_exceptions.py
│   └── events/
│       └── employee_events.py       # Domain events
│
├── application/                     # Use cases + DTOs + public services
│   ├── use_cases/
│   │   ├── list_employees.py
│   │   ├── create_employee.py
│   │   ├── update_employee.py
│   │   ├── delete_employee.py
│   │   └── bulk_actions.py
│   ├── dtos/
│   │   └── employee_dtos.py
│   └── services/
│       └── employee_leave_summary_service.py   # Public contract for other modules
│
├── infrastructure/                  # Django persistence
│   ├── models.py                    # ORM model only
│   ├── mappers/
│   │   └── employee_mapper.py       # ORM ↔ Domain
│   ├── repositories/
│   │   └── employee_repository.py   # Concrete implementation
│   └── migrations/
│
└── interfaces/
    └── api/
        ├── serializers.py           # Request / response shape
        ├── views.py                 # Thin viewsets → use cases
        ├── urls.py
        └── permissions.py
```

## Functional Coverage

| ID   | Requirement                                      | Status |
|------|--------------------------------------------------|--------|
| FR-1 | View all employees (paginated)                   | ✅     |
| FR-2 | Search employees by name                         | ✅     |
| FR-3 | Filter employees by department                   | ✅     |
| FR-4 | Add a new employee                               | ✅     |
| FR-5 | Edit an existing employee                        | ✅     |
| FR-6 | Delete (soft-delete) an employee                 | ✅     |
| FR-7 | Bulk actions (transfer / deactivate)             | ✅     |
| FR-8 | Employees on leave count via query service       | ✅     |
| FR-9 | Dashboard department metrics endpoint            | ✅     |

## Key Architectural Rules Observed

- **Domain layer is framework-agnostic** — no Django / DRF imports in entities, value objects, events or repository interfaces.
- **Use cases** orchestrate a single business operation and own the transaction boundary (`@transaction.atomic`).
- **Repository interface** (domain) is separated from the Django implementation (infrastructure).
- **Mappers** translate ORM ↔ domain entities; no ORM objects leak into application or domain.
- **DTOs** move data between layers.
- **Viewsets are thin** — only call use cases and serialize results.
- **Business validation** lives in the domain (Email VO, hire-date rules, name rules, etc.).
- **Other modules** must consume HR data only through `EmployeeLeaveSummaryService` (application-layer public contract). Never import `hr.infrastructure.models` or the concrete repository from outside HR.
- Domain events (`EmployeeCreated`, `EmployeeStatusChanged`, `EmployeeSoftDeleted`, …) are recorded on the aggregate and can be dispatched by an event bus / outbox later.

## Wiring into the Project

1. Add `"hr"` to `INSTALLED_APPS`.

2. Include the URLs:

```python
# project/urls.py
path("api/v1/hr/", include("hr.interfaces.api.urls")),
```

3. Run migrations:

```bash
python manage.py makemigrations hr
python manage.py migrate
```

4. (Optional) If you keep migrations under `infrastructure/migrations`:

```python
# settings.py
MIGRATION_MODULES = {
    "hr": "hr.infrastructure.migrations",
}
```

## API Endpoints

| Method | Path                                      | Description                        |
|--------|-------------------------------------------|------------------------------------|
| GET    | `/api/v1/hr/employees/`                   | List (search, department, page)    |
| GET    | `/api/v1/hr/employees/{id}/`              | Retrieve one                       |
| POST   | `/api/v1/hr/employees/`                   | Create                             |
| PUT/PATCH | `/api/v1/hr/employees/{id}/`           | Update                             |
| DELETE | `/api/v1/hr/employees/{id}/`              | Soft delete                        |
| POST   | `/api/v1/hr/employees/bulk-transfer/`     | Bulk department transfer           |
| POST   | `/api/v1/hr/employees/bulk-deactivate/`   | Bulk deactivate                    |
| GET    | `/api/v1/hr/leave-summary/`               | Count of employees on leave        |
| GET    | `/api/v1/hr/department-metrics/?department_id=` | Dashboard metrics             |

### Query parameters (list)

- `search` / `name` — free-text search on first name, last name, email
- `department` / `department_id` — filter by department UUID
- `page`, `page_size` — pagination (default page_size=20, max 100)

### Response envelope

All successful responses follow:

```json
{
  "success": true,
  "data": { ... },
  "message": "optional human message"
}
```

Errors:

```json
{
  "success": false,
  "error": {
    "code": "employee_not_found",
    "message": "..."
  }
}
```

## Unit-test friendly design

Domain entities and use cases can be unit-tested with a fake/in-memory repository
(no database required). The concrete `DjangoEmployeeRepository` is only used at
the composition root (the view).

## Notes / Assumptions

- Soft-delete is used (matching Inventory pattern).
- Department is referenced by UUID + denormalised name (no separate Department aggregate in this challenge scope).
- Leave status is a simple boolean + domain event; extend as needed for full leave management.
- Permissions are a placeholder (`IsHRStaff`); replace with your real RBAC.
- Domain events are collected on the aggregate (`pull_events()`) but not yet published to a bus — wire an outbox when ready.
