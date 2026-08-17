# InfoSys 22 Assignment 1 — Table Reservation System

A simple Django backend for managing restaurant table reservations.

The project includes **models, forms, views, and URLs**. HTML templates, CSS, JavaScript, and deployment are not included.

## How to Run

Open PowerShell:

```powershell
cd C:\Users\Laurence\table-reservation
.\.venv\Scripts\python.exe manage.py runserver
```

Then open:

**http://127.0.0.1:8000/**

Keep the terminal open while using the website. Press `Ctrl+C` to stop the server.

### First-Time Setup

If the project is copied to another computer:

```powershell
cd C:\Users\Laurence\table-reservation
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Project Files

The main submission files are in `reservation_app/`:

```text
reservation_app/
├── models.py
├── forms.py
├── views.py
├── urls.py
└── migrations/
```

## Models

The system has these models:

* **Customer** — stores customer information.
* **TableCategory** — stores table types such as Indoor, Outdoor, or VIP.
* **Table** — stores table number, category, capacity, and availability.
* **ReservationStatus** — stores reservation statuses.
* **Reservation** — stores customer bookings.
* **Payment** — stores payments for reservations.
* **AuditLog** — records reservation actions.

### Relationships

* A customer can have many reservations.
* A category can have many tables.
* A reservation has one customer, table, and status.
* A reservation can have many payments.
* A reservation can have many audit logs.

The following fields are unique:

* Customer email
* Category name
* Table number
* Status name

Most models have `created_at` and `updated_at`.

## Forms

The project has these forms:

* `CustomerForm`
* `TableCategoryForm`
* `TableForm`
* `ReservationStatusForm`
* `ReservationForm`
* `PaymentForm`

IDs and timestamps are not editable.

The reservation form includes date, time, and guest-count inputs.

### Reservation Validation

The reservation form checks that:

* Guests must be greater than 0.
* End time must be after start time.
* Guests cannot exceed table capacity.
* An unavailable table cannot be booked.
* A table cannot have overlapping reservations.
* Cancelled reservations do not count as conflicts.

Invalid reservations are not saved.

## Views

The system provides:

| Resource           | Available actions                    |
| ------------------ | ------------------------------------ |
| Customer           | List, detail, create, update, delete |
| Table category     | List, detail, create, update, delete |
| Table              | List, detail, create, update, delete |
| Reservation status | List, create, update, delete         |
| Reservation        | List, detail, create, update, cancel |
| Payment            | List, detail, create, update         |
| Audit log          | List, detail                         |

Deleting a category, table, or status that is still being used is blocked.

## Reservation Features

Reservations can be filtered by:

```text
/reservations/?customer=1
/reservations/?date=2026-08-20
```

Payments can be filtered by reservation:

```text
/payments/?reservation=1
```

Audit logs can also be filtered:

```text
/audit-logs/?reservation=1
```

When a reservation is:

* **Created** — an audit log is added.
* **Updated** — an audit log is added.
* **Cancelled** — its status changes to Cancelled and an audit log is added.

The reservation is not deleted when it is cancelled.

## URLs

| Path                         | Name                        |
| ---------------------------- | --------------------------- |
| `/`                          | `home`                      |
| `/customers/`                | `customer_list`             |
| `/customers/add/`            | `customer_create`           |
| `/customers/<id>/`           | `customer_detail`           |
| `/customers/<id>/edit/`      | `customer_update`           |
| `/customers/<id>/delete/`    | `customer_delete`           |
| `/table-categories/`         | `table_category_list`       |
| `/table-categories/add/`     | `table_category_create`     |
| `/tables/`                   | `table_list`                |
| `/tables/add/`               | `table_create`              |
| `/reservation-statuses/`     | `reservation_status_list`   |
| `/reservation-statuses/add/` | `reservation_status_create` |
| `/reservations/`             | `reservation_list`          |
| `/reservations/add/`         | `reservation_create`        |
| `/reservations/<id>/`        | `reservation_detail`        |
| `/reservations/<id>/edit/`   | `reservation_update`        |
| `/reservations/<id>/cancel/` | `reservation_cancel`        |
| `/payments/`                 | `payment_list`              |
| `/payments/add/`             | `payment_create`            |
| `/payments/<id>/`            | `payment_detail`            |
| `/payments/<id>/edit/`       | `payment_update`            |
| `/audit-logs/`               | `audit_log_list`            |
| `/audit-logs/<id>/`          | `audit_log_detail`          |

## Demo

A simple demonstration can be done in this order:

1. Create a table category.
2. Create a table with capacity 4.
3. Create a customer.
4. Create a reservation for 2 guests.
5. Check the reservation detail page and audit log.
6. Try an invalid reservation, such as 8 guests. An error should appear.
7. Filter reservations by customer.
8. Add a payment and filter payments by reservation.
9. Cancel the reservation.
10. Check that the status is **Cancelled** and a new audit log was created.

## Out of Scope

This assignment does not require:

* HTML template files
* CSS
* JavaScript
* Bootstrap or Tailwind
* Visual design
* Deployment

Django Admin is available for convenience but is not required.
