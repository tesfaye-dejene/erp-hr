# ERP HR Starter Project

Complete ready-to-run Django project with the **HR Employee Directory** module
(DDD / Clean Architecture) for the Backend Intern Challenge.

## Quick Start (VS Code)

### 1. Open the project
- Unzip this folder
- Open the folder in VS Code: `File → Open Folder`

### 2. Create virtual environment & install packages

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run migrations
```bash
python manage.py makemigrations hr
python manage.py migrate
```

### 4. (Optional) Create admin user
```bash
python manage.py createsuperuser
```

### 5. Start the server
```bash
python manage.py runserver
```

Open in browser:
- http://127.0.0.1:8000/                    → API root
- http://127.0.0.1:8000/api/v1/hr/employees/ → Employee list (Browsable API)
- http://127.0.0.1:8000/admin/              → Django admin

---

## Main API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/hr/employees/` | List employees (paginated) |
| GET | `/api/v1/hr/employees/?search=john` | Search by name |
| GET | `/api/v1/hr/employees/?department_id=<uuid>` | Filter by department |
| POST | `/api/v1/hr/employees/` | Create employee |
| GET | `/api/v1/hr/employees/<id>/` | Get one employee |
| PUT/PATCH | `/api/v1/hr/employees/<id>/` | Update employee |
| DELETE | `/api/v1/hr/employees/<id>/` | Soft-delete employee |
| POST | `/api/v1/hr/employees/bulk-transfer/` | Bulk transfer department |
| POST | `/api/v1/hr/employees/bulk-deactivate/` | Bulk deactivate |
| GET | `/api/v1/hr/leave-summary/` | Count of employees on leave |
| GET | `/api/v1/hr/department-metrics/?department_id=<uuid>` | Dashboard metrics |

### Example: Create an employee (POST body)

```json
{
  "first_name": "Abebe",
  "last_name": "Kebede",
  "email": "abebe.kebede@example.com",
  "department_id": "11111111-1111-1111-1111-111111111111",
  "department_name": "Engineering",
  "hire_date": "2024-01-15",
  "status": "active"
}
```

You can test all endpoints directly in the browser using the **Browsable API**
or with tools like Postman / Thunder Client / curl.

---

## Project Structure

```
erp_hr_starter/
├── manage.py
├── requirements.txt
├── README.md
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── hr/                     # HR module (DDD / Clean Architecture)
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── interfaces/
```

Permissions are currently **open** (AllowAny) so you can test without login.
Change this in `hr/interfaces/api/permissions.py` and `config/settings.py` later.
