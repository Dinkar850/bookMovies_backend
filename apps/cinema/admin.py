from django.contrib import admin

from .models import Cinema, Seat


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rows", "seats_per_row", "address", "city")
    list_filter = ("city",)
    search_fields = ("name", "address", "city__name")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "seat_row", "seat_number", "cinema")
    list_filter = ("cinema",)
