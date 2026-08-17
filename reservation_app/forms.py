from django import forms

from .models import (
    Customer,
    Payment,
    Reservation,
    ReservationStatus,
    Table,
    TableCategory,
)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone"]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "phone": "Phone number",
        }


class TableCategoryForm(forms.ModelForm):
    class Meta:
        model = TableCategory
        fields = ["name", "description"]
        labels = {
            "name": "Category name",
            "description": "Description",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["table_number", "category", "capacity", "is_available"]
        labels = {
            "table_number": "Table number",
            "category": "Table category",
            "capacity": "Seating capacity",
            "is_available": "Available for reservation",
        }
        widgets = {
            "capacity": forms.NumberInput(attrs={"min": 1}),
        }


class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = ReservationStatus
        fields = ["name", "description"]
        labels = {
            "name": "Status name",
            "description": "Description",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "customer",
            "table",
            "status",
            "reservation_date",
            "start_time",
            "end_time",
            "number_of_guests",
            "notes",
        ]
        labels = {
            "customer": "Customer",
            "table": "Table",
            "status": "Reservation status",
            "reservation_date": "Reservation date",
            "start_time": "Start time",
            "end_time": "End time",
            "number_of_guests": "Number of guests",
            "notes": "Notes",
        }
        widgets = {
            "reservation_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "number_of_guests": forms.NumberInput(attrs={"min": 1}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_number_of_guests(self):
        guests = self.cleaned_data.get("number_of_guests")
        if guests is not None and guests <= 0:
            raise forms.ValidationError("Number of guests must be positive.")
        return guests

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        guests = cleaned_data.get("number_of_guests")
        table = cleaned_data.get("table")
        reservation_date = cleaned_data.get("reservation_date")

        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be later than start time.")

        if table and guests and guests > table.capacity:
            self.add_error(
                "number_of_guests",
                f"Selected table can only accommodate {table.capacity} guests.",
            )

        if table and not table.is_available:
            self.add_error("table", "Selected table is not available for reservation.")

        if table and reservation_date and start_time and end_time:
            overlapping = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
            ).exclude(status__name__iexact="Cancelled")
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            for other in overlapping:
                if start_time < other.end_time and end_time > other.start_time:
                    self.add_error(
                        "table",
                        "This table is already reserved for the selected date and time.",
                    )
                    break

        return cleaned_data


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "reservation",
            "amount",
            "payment_method",
            "payment_status",
            "reference_number",
        ]
        labels = {
            "reservation": "Reservation",
            "amount": "Amount",
            "payment_method": "Payment method",
            "payment_status": "Payment status",
            "reference_number": "Reference number",
        }
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
