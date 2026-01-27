from django.contrib import admin

from .models import Cinema


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rows", "seats_per_row", "address", "city")
    list_filter = ("city",)
    search_fields = ("name", "address")
