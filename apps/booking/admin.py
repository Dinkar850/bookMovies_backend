from django.contrib import admin

from .forms import BookingAdminForm
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = ("id", "status", "user", "slot")
    list_filter = ("status", "user")
    search_fields = ("user__email",)
    filter_horizontal = ("seat",)
    list_select_related = ("user", "slot__movie", "slot__cinema__city")
