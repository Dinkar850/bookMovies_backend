from django.contrib import admin

from apps.cinema.models import Cinema, Seat


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "city", "rows", "seats_per_row")
    list_filter = ("city",)
    search_fields = ("name", "address", "city__name")
    list_select_related = ("city",)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "seat_row",
        "seat_number",
        "cinema",
        "cinema__city",
    )
    list_filter = ("cinema", "cinema__city", "is_active")
    search_fields = (
        "cinema__name",
        "cinema__city__name",
    )
    list_select_related = ("cinema__city",)
    readonly_fields = ("seat_row", "seat_number", "cinema")

    def has_add_permission(self, request):
        """Restricts seat addition from admin"""

        return False
