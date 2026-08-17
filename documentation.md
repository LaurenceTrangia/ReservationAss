# InfoSys 22 Assignment 1 — Table Reservation System

Django backend for a restaurant table reservation system. Scope is **models, forms, views, and URLs only**. HTML template files, CSS, JavaScript, and deployment are not part of this activity.

The application still returns simple HTML from the views so pages and forms can be used in a browser.

## How to run

From PowerShell:

```powershell
cd C:\Users\Laurence\table-reservation
.\.venv\Scripts\python.exe manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Leave that terminal open while using the site. Stop the server with `Ctrl+C`.

To activate the virtual environment first:

```powershell
cd C:\Users\Laurence\table-reservation
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

### First-time setup (already done in this folder)

If you copy the project to another machine:

```powershell
cd C:\Users\Laurence\table-reservation
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Migrations for this copy have already been applied. Evidence is in `MIGRATION_EVIDENCE.txt`.

## Project layout

```text
table-reservation/
├── manage.py
├── requirements.txt
├── MIGRATION_EVIDENCE.txt
├── documentation.md
├── table_reservation/          # Django project settings
│   ├── settings.py
│   └── urls.py                 # includes reservation_app.urls
└── reservation_app/            # required submission app
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    └── migrations/
```

Required submission files live under `reservation_app/`.

## How the pieces connect

A request follows this path:

**URL → view → form (on create/update) → model → database**

1. The project `table_reservation/urls.py` sends non-admin paths to `reservation_app.urls`.
2. The app `urls.py` matches the path to a named view (`app_name = "reservation_app"`).
3. List and detail views read models and return a page.
4. Create and update views bind a `ModelForm`. If `form.is_valid()` is true, the record is saved. If not, the same page is shown with validation errors and nothing is written.
5. Reservation create, update, and cancel also insert an `AuditLog` row in code (there is no public audit form).

That is the assignment pipeline: **ERD → Models → Forms → Views → URLs**.

## Models

| Model | Purpose |
| --- | --- |
| `Customer` | Person who books a table |
| `TableCategory` | Type of table (for example Indoor, Outdoor, VIP) |
| `Table` | One reservable table, with capacity |
| `ReservationStatus` | Standardized status (Pending, Confirmed, Cancelled, Completed) |
| `Reservation` | One booking: customer, table, status, date, times, guest count |
| `Payment` | Payment linked to a reservation |
| `AuditLog` | Record of important reservation actions |

### Relationships

- One customer has many reservations (`Reservation.customer`).
- One category has many tables (`Table.category`).
- One reservation belongs to one customer, one table, and one status.
- One reservation can have many payments (`Payment.reservation`).
- One reservation can have many audit logs (`AuditLog.reservation`).

Unique fields: customer email, category name, table number, status name.

Most models have `created_at` and `updated_at`. `AuditLog` only has `created_at` because logs are not edited.

Statuses **Pending**, **Confirmed**, **Cancelled**, and **Completed** are seeded by migration `0002_seed_reservation_statuses`.

## Forms

| Form | Editable fields |
| --- | --- |
| `CustomerForm` | first name, last name, email, phone |
| `TableCategoryForm` | name, description |
| `TableForm` | table number, category, capacity, available |
| `ReservationStatusForm` | name, description |
| `ReservationForm` | customer, table, status, date, start time, end time, guests, notes |
| `PaymentForm` | reservation, amount, method, status, reference |

IDs and timestamps are excluded. `AuditLog` has no public form.

`ReservationForm` widgets:

- date picker for reservation date
- time pickers for start and end time
- number input for guest count

### Reservation validation

Invalid data is rejected by the form and is not saved:

- number of guests must be positive
- end time must be later than start time
- guest count cannot exceed the selected table’s capacity
- unavailable tables cannot be booked
- the same table cannot be double-booked for overlapping times on the same date (cancelled reservations are ignored)

## Views

Each resource has the views required by the checklist.

| Resource | Views |
| --- | --- |
| Customer | list, detail, create, update, delete |
| Table category | list, detail, create, update, delete |
| Table | list, detail, create, update, delete |
| Reservation status | list, create, update, delete (no detail page) |
| Reservation | list, detail, create, update, cancel |
| Payment | list, detail, create, update |
| Audit log | list, detail |

### Extra reservation behaviour

- Filter reservations by customer: `/reservations/?customer=1`
- Filter reservations by date: `/reservations/?date=2026-08-20`
- Filter payments by reservation: `/payments/?reservation=1`
- Filter audit logs by reservation: `/audit-logs/?reservation=1`
- Cancel sets status to **Cancelled** and writes an audit row (the row is not deleted).
- Create and update also write audit rows (`created` / `updated`).

Deleting a table, category, or status that is still in use is blocked (`PROTECT`) and the view shows an error instead of breaking.

## URLs

All routes are named and use `<int:pk>` for IDs.

| Path | Name |
| --- | --- |
| `/` | `home` |
| `/customers/` | `customer_list` |
| `/customers/add/` | `customer_create` |
| `/customers/<id>/` | `customer_detail` |
| `/customers/<id>/edit/` | `customer_update` |
| `/customers/<id>/delete/` | `customer_delete` |
| `/table-categories/` | `table_category_list` |
| `/table-categories/add/` | `table_category_create` |
| `/table-categories/<id>/` | `table_category_detail` |
| `/table-categories/<id>/edit/` | `table_category_update` |
| `/table-categories/<id>/delete/` | `table_category_delete` |
| `/tables/` | `table_list` |
| `/tables/add/` | `table_create` |
| `/tables/<id>/` | `table_detail` |
| `/tables/<id>/edit/` | `table_update` |
| `/tables/<id>/delete/` | `table_delete` |
| `/reservation-statuses/` | `reservation_status_list` |
| `/reservation-statuses/add/` | `reservation_status_create` |
| `/reservation-statuses/<id>/edit/` | `reservation_status_update` |
| `/reservation-statuses/<id>/delete/` | `reservation_status_delete` |
| `/reservations/` | `reservation_list` |
| `/reservations/add/` | `reservation_create` |
| `/reservations/<id>/` | `reservation_detail` |
| `/reservations/<id>/edit/` | `reservation_update` |
| `/reservations/<id>/cancel/` | `reservation_cancel` |
| `/payments/` | `payment_list` |
| `/payments/add/` | `payment_create` |
| `/payments/<id>/` | `payment_detail` |
| `/payments/<id>/edit/` | `payment_update` |
| `/audit-logs/` | `audit_log_list` |
| `/audit-logs/<id>/` | `audit_log_detail` |

Named reverse example: `redirect("reservation_app:reservation_detail", pk=reservation.pk)`.

## Suggested demo walkthrough

1. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
2. Add a **table category**, then a **table** with capacity 4.
3. Add a **customer**.
4. Add a **reservation** with 2 guests and a valid time range. It should save, and an audit log should appear on the reservation detail page.
5. Try the same form with 8 guests, or an end time before the start time. The form should show errors and not save.
6. Open `/reservations/?customer=1` to filter by customer.
7. Add a **payment** for that reservation, then open `/payments/?reservation=1`.
8. Cancel the reservation. Status becomes **Cancelled** and another audit row is created.

## What is out of scope

Per the assignment:

- `templates/`
- CSS / JavaScript / Bootstrap / Tailwind
- visual design
- deployment

Django admin is registered for convenience but is not a required deliverable. Use `/admin/` only if you create a superuser.
