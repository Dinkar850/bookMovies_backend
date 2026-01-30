from django.contrib import admin

from .models import Slot


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
        "schedule",
        "end_time",
        "price",
        "movie",
        "cinema",
        "language",
    )
    list_filter = ("language", "is_active")
    search_fields = ("movie__name", "cinema__name")
