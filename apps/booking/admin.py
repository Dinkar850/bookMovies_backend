from django.contrib import admin

from apps.booking.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "user",
        "status",
        "slot",
        "slot__movie",
        "slot__language",
        "slot__cinema",
        "slot__cinema__city",
    )
    list_filter = ("status", "slot__movie", "slot__cinema", "slot__cinema__city")
    search_fields = ("user__email",)
    readonly_fields = ("slot", "user", "seats")
    list_select_related = (
        "user",
        "slot__movie",
        "slot__cinema__city",
        "slot__language",
    )

    def has_add_permission(self, request):
        """Restricts booking creation from admin panel"""

        return False
