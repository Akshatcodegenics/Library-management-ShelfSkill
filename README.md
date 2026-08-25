# Production Library Management System

A high-performance, production-style Library Management System built strictly using **Python 3.11+**, **Django 5**, **Django REST Framework (DRF)**, **SimpleJWT**, and **Bootstrap 5**.

---

## 🌟 Key System Capabilities

- **Strict Django/Python Backend Architecture**: Decoupled RESTful APIs combined with server-rendered HTML views and Vanilla JavaScript `fetch()` clients.
- **Role-Based Access Control (RBAC)**: Custom Django `User` model extending `AbstractUser` with strict `AUTHOR` and `MEMBER` roles enforced at the DRF permission level.
- **Database Transaction Safety**: Borrowing and returning operations are guarded using `django.db.transaction.atomic()` and `select_for_update()` row-level locks to prevent race conditions and inventory corruption under concurrent access.
- **Model-Level & DB Constraints**: `CheckConstraint` for copy counts (`available_copies <= total_copies` and `available_copies >= 0`) along with `UniqueConstraint` on ISBN numbers and emails.
- **Dynamic Overdue Tracking**: Real-time evaluation of overdue items without relying on periodic manual database flags.
- **Full OpenAPI / Swagger Support**: Interactive API documentation generated using `drf-spectacular`.
- **Postman Integration**: Exported Postman collection with token variables and environment configurations.
- **Comprehensive Test Suite**: Automated unit and integration test coverage for authentication, RBAC, borrowing rules, returning limits, and transaction concurrency.

---

## 🛠️ Technology Stack

- **Core Backend**: Python 3.11+, Django 5.x
- **API Framework**: Django REST Framework (DRF)
- **Authentication**: `djangorestframework-simplejwt` (JWT Access & Refresh Tokens)
- **Database**: PostgreSQL (Preferred for production) / SQLite3 (Zero-config local fallback)
- **Filtering & Search**: `django-filter`, DRF `SearchFilter`, `OrderingFilter`
- **Documentation**: `drf-spectacular` (Swagger UI & ReDoc)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript (`fetch()` with automated JWT refresh interceptor)

---

## 📁 Project Structure

```
library-management-system/
│
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── library/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── services.py
│   ├── filters.py
│   ├── views.py
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   └── tests.py
│
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   └── apps.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── author/
│   │   ├── dashboard.html
│   │   ├── books.html
│   │   └── book-form.html
│   └── member/
│       ├── dashboard.html
│       ├── books.html
│       ├── book-detail.html
│       ├── borrowed-books.html
│       ├── history.html
│       └── overdue.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js
│       ├── author.js
│       └── member.js
│
└── postman/
    └── Library-Management-System.postman_collection.json
```

---

## ⚡ Setup & Installation Instructions

### 1. Prerequisites
Ensure you have **Python 3.11+** installed on your system.

### 2. Virtual Environment Setup

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Copy `.env.example` to `.env` if custom configurations are needed:
```bash
cp .env.example .env
```

*Note: By default, if PostgreSQL database credentials are not supplied in `.env`, the system automatically falls back to local SQLite database (`db.sqlite3`).*

### 5. Database Migrations
Generate and apply database migrations:
```bash
python manage.py makemigrations accounts library dashboard
python manage.py migrate
```

### 6. Seed Sample Data (Development Dataset)
Execute the custom seeding command to populate initial authors, books, members, and sample loan records:
```bash
python manage.py seed_data
```

### 7. Run Local Server
```bash
python manage.py runserver
```

The Web Application will be available at: **`http://127.0.0.1:8000/`**

---

## 🔑 Seed Development Credentials

> [!IMPORTANT]
> The following credentials are generated for development testing only.

| Role | Username / Email | Password | Access Portal |
|------|------------------|----------|---------------|
| **System Admin** | `admin` | `adminpassword123` | `/admin/` |
| **Author** | `author@example.com` | `password123` | `/author/dashboard/` |
| **Member** | `member@example.com` | `password123` | `/member/dashboard/` |

---

## 🔒 Role-Based Authorization Rules (RBAC)

| Resource Action | AUTHOR Role | MEMBER Role | Server-side Enforcement |
|-----------------|-------------|-------------|-------------------------|
| **Access Author Portal** | ✅ Allowed | ❌ Forbidden | `IsAuthor` permission class |
| **Create / Edit / Delete Books** | ✅ Allowed (Own books) | ❌ Forbidden | `IsBookOwnerAuthorOrReadOnly` |
| **View Catalogue** | ✅ Allowed | ✅ Allowed | Read-only permissions |
| **Borrow Books** | ❌ Forbidden | ✅ Allowed | `IsMember` permission class |
| **Return Books** | ❌ Forbidden | ✅ Allowed (Own loans) | `IsMember` + `ReturnService` check |
| **View Loan History** | ❌ Forbidden | ✅ Allowed (Own history) | `IsMemberSelfOrAdmin` |

---

## 📖 API Documentation & Postman

### Interactive OpenAPI Documentation
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema (JSON)**: `http://127.0.0.1:8000/api/schema/`

### Postman Collection
Import the file [`postman/Library-Management-System.postman_collection.json`](file:///c:/Users/asus/Downloads/ppe-safety-system/library/postman/Library-Management-System.postman_collection.json) into Postman. It contains pre-configured requests for Authentication, Authors, Books, Members, Borrowing, Returning, Overdue, and Dashboard APIs.

---

## 🧪 Running Unit & Integration Tests

Run the full Django test suite:
```bash
python manage.py test
```

### Verified Test Cases:
1. `test_register_author` & `test_register_member`
2. `test_author_can_create_book` & `test_member_cannot_create_book`
3. `test_duplicate_isbn_rejected` & `test_duplicate_email_rejected`
4. `test_author_cannot_modify_other_authors_book`
5. `test_successful_borrow_decreases_available_copies`
6. `test_duplicate_active_borrowing_rejected`
7. `test_inactive_member_blocked_from_borrowing`
8. `test_borrowing_when_no_copies_available`
9. `test_successful_return_increases_available_copies`
10. `test_cannot_return_already_returned_record`
11. `test_member_cannot_return_another_members_book`
12. `test_member_cannot_view_another_members_history`
13. `test_overdue_detection`
