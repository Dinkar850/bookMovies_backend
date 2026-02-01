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
        "cinema__city",
        "language",
    )
    list_filter = ("language", "is_active")
    search_fields = ("movie__name", "cinema__name")
    list_select_related = ("movie", "cinema__city", "language")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # Adds city to each cinema in the cinema field along with its name and address in the form
        if db_field.name == "cinema":
            field.label_from_instance = (
                lambda obj: f"{obj.name}, {obj.address}, {obj.city.name}"
            )

        return field
