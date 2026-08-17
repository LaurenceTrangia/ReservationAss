from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TableCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "table categories"

    def __str__(self):
        return self.name


class Table(models.Model):
    table_number = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(
        TableCategory,
        on_delete=models.PROTECT,
        related_name="tables",
    )
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} ({self.capacity} seats)"


class ReservationStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "reservation statuses"

    def __str__(self):
        return self.name


class Reservation(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    status = models.ForeignKey(
        ReservationStatus,
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-reservation_date", "start_time"]

    def __str__(self):
        return (
            f"Reservation {self.pk} — {self.customer} on "
            f"{self.reservation_date} ({self.start_time}-{self.end_time})"
        )

    def clean(self):
        errors = {}

        if self.number_of_guests is not None and self.number_of_guests < 1:
            errors["number_of_guests"] = "Number of guests must be positive."

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            errors["end_time"] = "End time must be later than start time."

        if self.table_id and self.number_of_guests:
            if self.number_of_guests > self.table.capacity:
                errors["number_of_guests"] = (
                    f"Selected table can only accommodate {self.table.capacity} guests."
                )
            if not self.table.is_available:
                errors["table"] = "Selected table is not available for reservation."

        if (
            self.table_id
            and self.reservation_date
            and self.start_time
            and self.end_time
        ):
            overlapping = Reservation.objects.filter(
                table=self.table,
                reservation_date=self.reservation_date,
            ).exclude(status__name__iexact="Cancelled")
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            for other in overlapping:
                if self.start_time < other.end_time and self.end_time > other.start_time:
                    errors["table"] = (
                        "This table is already reserved for the selected date and time."
                    )
                    break

        if errors:
            raise ValidationError(errors)


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        ONLINE = "online", "Online"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    payment_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reference_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.pk} for reservation {self.reservation_id} ({self.amount})"


class AuditLog(models.Model):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — reservation {self.reservation_id} at {self.created_at}"
