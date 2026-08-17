from django.contrib import admin

from .models import (
    AuditLog,
    Customer,
    Payment,
    Reservation,
    ReservationStatus,
    Table,
    TableCategory,
)

admin.site.register(Customer)
admin.site.register(TableCategory)
admin.site.register(Table)
admin.site.register(ReservationStatus)
admin.site.register(Reservation)
admin.site.register(Payment)
admin.site.register(AuditLog)
