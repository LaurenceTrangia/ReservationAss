from html import escape

from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .forms import (
    CustomerForm,
    PaymentForm,
    ReservationForm,
    ReservationStatusForm,
    TableCategoryForm,
    TableForm,
)
from .models import (
    AuditLog,
    Customer,
    Payment,
    Reservation,
    ReservationStatus,
    Table,
    TableCategory,
)


def _page(title, body, status=200):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)}</title>
</head>
<body>
  <nav>
    <a href="{reverse("reservation_app:home")}">Home</a> |
    <a href="{reverse("reservation_app:customer_list")}">Customers</a> |
    <a href="{reverse("reservation_app:table_category_list")}">Table categories</a> |
    <a href="{reverse("reservation_app:table_list")}">Tables</a> |
    <a href="{reverse("reservation_app:reservation_status_list")}">Reservation statuses</a> |
    <a href="{reverse("reservation_app:reservation_list")}">Reservations</a> |
    <a href="{reverse("reservation_app:payment_list")}">Payments</a> |
    <a href="{reverse("reservation_app:audit_log_list")}">Audit logs</a>
  </nav>
  <h1>{escape(title)}</h1>
  {body}
</body>
</html>"""
    return HttpResponse(html, status=status)


def _csrf_form(request, inner_html, action_label="Save"):
    from django.middleware.csrf import get_token

    token = get_token(request)
    return (
        f'<form method="post">'
        f'<input type="hidden" name="csrfmiddlewaretoken" value="{escape(token)}">'
        f"{inner_html}"
        f'<p><button type="submit">{escape(action_label)}</button></p>'
        f"</form>"
    )


def _model_form(request, form, action_label="Save"):
    return _csrf_form(request, form.as_p(), action_label)


def _link_list(items):
    if not items:
        return "<p>No records found.</p>"
    rows = "".join(f"<li>{item}</li>" for item in items)
    return f"<ul>{rows}</ul>"


def _record_audit(reservation, action, details=""):
    AuditLog.objects.create(reservation=reservation, action=action, details=details)


def _get_or_create_status(name):
    status, _ = ReservationStatus.objects.get_or_create(
        name=name,
        defaults={"description": f"{name} reservation"},
    )
    return status


def home(request):
    body = """
    <p>Django Table Reservation System — backend only (models, forms, views, URLs).</p>
    <ul>
      <li><a href="/customers/">Customers</a></li>
      <li><a href="/table-categories/">Table categories</a></li>
      <li><a href="/tables/">Tables</a></li>
      <li><a href="/reservation-statuses/">Reservation statuses</a></li>
      <li><a href="/reservations/">Reservations</a></li>
      <li><a href="/payments/">Payments</a></li>
      <li><a href="/audit-logs/">Audit logs</a></li>
    </ul>
    """
    return _page("Table Reservation System", body)


# --- Customer ---


def customer_list(request):
    items = [
        (
            f'<a href="{reverse("reservation_app:customer_detail", args=[c.pk])}">'
            f"{escape(str(c))}</a> — {escape(c.email)}"
        )
        for c in Customer.objects.all()
    ]
    add = f'<p><a href="{reverse("reservation_app:customer_create")}">Add customer</a></p>'
    return _page("Customers", add + _link_list(items))


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    reservations = "".join(
        f'<li><a href="{reverse("reservation_app:reservation_detail", args=[r.pk])}">'
        f"{escape(str(r))}</a></li>"
        for r in customer.reservations.all()
    ) or "<li>No reservations.</li>"
    body = f"""
    <p>Email: {escape(customer.email)}<br>Phone: {escape(customer.phone)}</p>
    <p>
      <a href="{reverse("reservation_app:customer_update", args=[pk])}">Edit</a> |
      <a href="{reverse("reservation_app:customer_delete", args=[pk])}">Delete</a> |
      <a href="{reverse("reservation_app:reservation_list")}?customer={pk}">View reservations</a>
    </p>
    <h2>Reservations</h2>
    <ul>{reservations}</ul>
    """
    return _page(str(customer), body)


def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect("reservation_app:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return _page("Add customer", _model_form(request, form, "Create"))


def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:customer_detail", pk=pk)
    else:
        form = CustomerForm(instance=customer)
    return _page(f"Edit {customer}", _model_form(request, form, "Update"))


def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("reservation_app:customer_list")
    body = _csrf_form(
        request,
        f"<p>Delete {escape(str(customer))}? This also deletes their reservations.</p>",
        "Delete",
    )
    return _page("Delete customer", body)


# --- Table category ---


def table_category_list(request):
    items = [
        (
            f'<a href="{reverse("reservation_app:table_category_detail", args=[c.pk])}">'
            f"{escape(c.name)}</a>"
        )
        for c in TableCategory.objects.all()
    ]
    add = f'<p><a href="{reverse("reservation_app:table_category_create")}">Add category</a></p>'
    return _page("Table categories", add + _link_list(items))


def table_category_detail(request, pk):
    category = get_object_or_404(TableCategory, pk=pk)
    tables = "".join(
        f'<li><a href="{reverse("reservation_app:table_detail", args=[t.pk])}">'
        f"{escape(str(t))}</a></li>"
        for t in category.tables.all()
    ) or "<li>No tables in this category.</li>"
    body = f"""
    <p>{escape(category.description or "No description.")}</p>
    <p>
      <a href="{reverse("reservation_app:table_category_update", args=[pk])}">Edit</a> |
      <a href="{reverse("reservation_app:table_category_delete", args=[pk])}">Delete</a>
    </p>
    <h2>Tables</h2>
    <ul>{tables}</ul>
    """
    return _page(category.name, body)


def table_category_create(request):
    if request.method == "POST":
        form = TableCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return redirect("reservation_app:table_category_detail", pk=category.pk)
    else:
        form = TableCategoryForm()
    return _page("Add table category", _model_form(request, form, "Create"))


def table_category_update(request, pk):
    category = get_object_or_404(TableCategory, pk=pk)
    if request.method == "POST":
        form = TableCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:table_category_detail", pk=pk)
    else:
        form = TableCategoryForm(instance=category)
    return _page(f"Edit {category}", _model_form(request, form, "Update"))


def table_category_delete(request, pk):
    category = get_object_or_404(TableCategory, pk=pk)
    if request.method == "POST":
        try:
            category.delete()
        except ProtectedError:
            return _page(
                "Delete table category",
                "<p>Cannot delete this category while tables are assigned to it.</p>",
                status=400,
            )
        return redirect("reservation_app:table_category_list")
    body = _csrf_form(request, f"<p>Delete {escape(category.name)}?</p>", "Delete")
    return _page("Delete table category", body)


# --- Table ---


def table_list(request):
    items = [
        (
            f'<a href="{reverse("reservation_app:table_detail", args=[t.pk])}">'
            f"{escape(str(t))}</a> — {escape(t.category.name)}"
        )
        for t in Table.objects.select_related("category")
    ]
    add = f'<p><a href="{reverse("reservation_app:table_create")}">Add table</a></p>'
    return _page("Tables", add + _link_list(items))


def table_detail(request, pk):
    table = get_object_or_404(Table.objects.select_related("category"), pk=pk)
    body = f"""
    <p>
      Category: {escape(table.category.name)}<br>
      Capacity: {table.capacity}<br>
      Available: {"yes" if table.is_available else "no"}
    </p>
    <p>
      <a href="{reverse("reservation_app:table_update", args=[pk])}">Edit</a> |
      <a href="{reverse("reservation_app:table_delete", args=[pk])}">Delete</a>
    </p>
    """
    return _page(str(table), body)


def table_create(request):
    if request.method == "POST":
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save()
            return redirect("reservation_app:table_detail", pk=table.pk)
    else:
        form = TableForm()
    return _page("Add table", _model_form(request, form, "Create"))


def table_update(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == "POST":
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:table_detail", pk=pk)
    else:
        form = TableForm(instance=table)
    return _page(f"Edit {table}", _model_form(request, form, "Update"))


def table_delete(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == "POST":
        try:
            table.delete()
        except ProtectedError:
            return _page(
                "Delete table",
                "<p>Cannot delete this table while reservations are linked to it.</p>",
                status=400,
            )
        return redirect("reservation_app:table_list")
    body = _csrf_form(request, f"<p>Delete {escape(str(table))}?</p>", "Delete")
    return _page("Delete table", body)


# --- Reservation status ---


def reservation_status_list(request):
    items = [
        (
            f"{escape(s.name)} — "
            f'<a href="{reverse("reservation_app:reservation_status_update", args=[s.pk])}">Edit</a> | '
            f'<a href="{reverse("reservation_app:reservation_status_delete", args=[s.pk])}">Delete</a>'
        )
        for s in ReservationStatus.objects.all()
    ]
    add = (
        f'<p><a href="{reverse("reservation_app:reservation_status_create")}">'
        f"Add status</a></p>"
    )
    return _page("Reservation statuses", add + _link_list(items))


def reservation_status_create(request):
    if request.method == "POST":
        form = ReservationStatusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:reservation_status_list")
    else:
        form = ReservationStatusForm()
    return _page("Add reservation status", _model_form(request, form, "Create"))


def reservation_status_update(request, pk):
    status = get_object_or_404(ReservationStatus, pk=pk)
    if request.method == "POST":
        form = ReservationStatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:reservation_status_list")
    else:
        form = ReservationStatusForm(instance=status)
    return _page(f"Edit {status}", _model_form(request, form, "Update"))


def reservation_status_delete(request, pk):
    status = get_object_or_404(ReservationStatus, pk=pk)
    if request.method == "POST":
        try:
            status.delete()
        except ProtectedError:
            return _page(
                "Delete reservation status",
                "<p>Cannot delete this status while reservations are using it.</p>",
                status=400,
            )
        return redirect("reservation_app:reservation_status_list")
    body = _csrf_form(request, f"<p>Delete {escape(status.name)}?</p>", "Delete")
    return _page("Delete reservation status", body)


# --- Reservation ---


def reservation_list(request):
    reservations = Reservation.objects.select_related("customer", "table", "status")
    customer_id = request.GET.get("customer")
    date = request.GET.get("date")
    if customer_id:
        reservations = reservations.filter(customer_id=customer_id)
    if date:
        reservations = reservations.filter(reservation_date=date)

    items = [
        (
            f'<a href="{reverse("reservation_app:reservation_detail", args=[r.pk])}">'
            f"{escape(str(r))}</a> — {escape(r.status.name)}"
        )
        for r in reservations
    ]
    add = f'<p><a href="{reverse("reservation_app:reservation_create")}">Add reservation</a></p>'
    filters = """
    <form method="get">
      <label>Customer ID <input type="number" name="customer" min="1"></label>
      <label>Date <input type="date" name="date"></label>
      <button type="submit">Filter</button>
    </form>
    """
    return _page("Reservations", add + filters + _link_list(items))


def reservation_detail(request, pk):
    reservation = get_object_or_404(
        Reservation.objects.select_related("customer", "table", "status"),
        pk=pk,
    )
    payments = "".join(
        f'<li><a href="{reverse("reservation_app:payment_detail", args=[p.pk])}">'
        f"{escape(str(p))}</a></li>"
        for p in reservation.payments.all()
    ) or "<li>No payments.</li>"
    logs = "".join(
        f'<li><a href="{reverse("reservation_app:audit_log_detail", args=[log.pk])}">'
        f"{escape(str(log))}</a></li>"
        for log in reservation.audit_logs.all()
    ) or "<li>No audit logs.</li>"
    body = f"""
    <p>
      Customer: <a href="{reverse("reservation_app:customer_detail", args=[reservation.customer_id])}">
      {escape(str(reservation.customer))}</a><br>
      Table: <a href="{reverse("reservation_app:table_detail", args=[reservation.table_id])}">
      {escape(str(reservation.table))}</a><br>
      Status: {escape(reservation.status.name)}<br>
      Date: {reservation.reservation_date}<br>
      Time: {reservation.start_time} – {reservation.end_time}<br>
      Guests: {reservation.number_of_guests}
    </p>
    <p>
      <a href="{reverse("reservation_app:reservation_update", args=[pk])}">Edit</a> |
      <a href="{reverse("reservation_app:reservation_cancel", args=[pk])}">Cancel</a> |
      <a href="{reverse("reservation_app:payment_list")}?reservation={pk}">Payments</a> |
      <a href="{reverse("reservation_app:audit_log_list")}?reservation={pk}">Audit logs</a>
    </p>
    <h2>Payments</h2>
    <ul>{payments}</ul>
    <h2>Audit logs</h2>
    <ul>{logs}</ul>
    """
    return _page(f"Reservation {pk}", body)


def reservation_create(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            _record_audit(
                reservation,
                "created",
                f"Reservation created for {reservation.customer} at table {reservation.table}.",
            )
            return redirect("reservation_app:reservation_detail", pk=reservation.pk)
    else:
        form = ReservationForm()
    return _page("Add reservation", _model_form(request, form, "Create"))


def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save()
            _record_audit(
                reservation,
                "updated",
                f"Reservation {reservation.pk} was updated.",
            )
            return redirect("reservation_app:reservation_detail", pk=pk)
    else:
        form = ReservationForm(instance=reservation)
    return _page(f"Edit reservation {pk}", _model_form(request, form, "Update"))


def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == "POST":
        reservation.status = _get_or_create_status("Cancelled")
        reservation.save(update_fields=["status", "updated_at"])
        _record_audit(reservation, "cancelled", f"Reservation {reservation.pk} was cancelled.")
        return redirect("reservation_app:reservation_detail", pk=pk)
    body = _csrf_form(
        request,
        f"<p>Cancel reservation {pk} for {escape(str(reservation.customer))}?</p>",
        "Cancel reservation",
    )
    return _page("Cancel reservation", body)


# --- Payment ---


def payment_list(request):
    payments = Payment.objects.select_related("reservation")
    reservation_id = request.GET.get("reservation")
    if reservation_id:
        payments = payments.filter(reservation_id=reservation_id)
    items = [
        (
            f'<a href="{reverse("reservation_app:payment_detail", args=[p.pk])}">'
            f"{escape(str(p))}</a> — {escape(p.get_payment_status_display())}"
        )
        for p in payments
    ]
    add = f'<p><a href="{reverse("reservation_app:payment_create")}">Add payment</a></p>'
    filters = """
    <form method="get">
      <label>Reservation ID <input type="number" name="reservation" min="1"></label>
      <button type="submit">Filter</button>
    </form>
    """
    return _page("Payments", add + filters + _link_list(items))


def payment_detail(request, pk):
    payment = get_object_or_404(Payment.objects.select_related("reservation"), pk=pk)
    body = f"""
    <p>
      Reservation:
      <a href="{reverse("reservation_app:reservation_detail", args=[payment.reservation_id])}">
      {escape(str(payment.reservation))}</a><br>
      Amount: {payment.amount}<br>
      Method: {escape(payment.get_payment_method_display())}<br>
      Status: {escape(payment.get_payment_status_display())}<br>
      Reference: {escape(payment.reference_number or "—")}
    </p>
    <p><a href="{reverse("reservation_app:payment_update", args=[pk])}">Edit</a></p>
    """
    return _page(f"Payment {pk}", body)


def payment_create(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            return redirect("reservation_app:payment_detail", pk=payment.pk)
    else:
        initial = {}
        reservation_id = request.GET.get("reservation")
        if reservation_id:
            initial["reservation"] = reservation_id
        form = PaymentForm(initial=initial)
    return _page("Add payment", _model_form(request, form, "Create"))


def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect("reservation_app:payment_detail", pk=pk)
    else:
        form = PaymentForm(instance=payment)
    return _page(f"Edit payment {pk}", _model_form(request, form, "Update"))


# --- Audit log ---


def audit_log_list(request):
    logs = AuditLog.objects.select_related("reservation")
    reservation_id = request.GET.get("reservation")
    if reservation_id:
        logs = logs.filter(reservation_id=reservation_id)
    items = [
        (
            f'<a href="{reverse("reservation_app:audit_log_detail", args=[log.pk])}">'
            f"{escape(str(log))}</a>"
        )
        for log in logs
    ]
    filters = """
    <form method="get">
      <label>Reservation ID <input type="number" name="reservation" min="1"></label>
      <button type="submit">Filter</button>
    </form>
    """
    return _page("Audit logs", filters + _link_list(items))


def audit_log_detail(request, pk):
    log = get_object_or_404(AuditLog.objects.select_related("reservation"), pk=pk)
    body = f"""
    <p>
      Reservation:
      <a href="{reverse("reservation_app:reservation_detail", args=[log.reservation_id])}">
      {escape(str(log.reservation))}</a><br>
      Action: {escape(log.action)}<br>
      Details: {escape(log.details or "—")}<br>
      Created: {log.created_at}
    </p>
    """
    return _page(f"Audit log {pk}", body)
