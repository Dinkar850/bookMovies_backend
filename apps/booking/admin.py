# admin.py
from django.contrib import admin

from .models import Booking, Seat


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "user", "slot")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "seat_row", "seat_number")
    list_filter = ("booking__status",)
