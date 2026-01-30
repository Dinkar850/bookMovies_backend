from django.contrib import admin

from .forms import BookingAdminForm
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = ("id", "status", "user", "slot")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    filter_horizontal = ("seat",)
