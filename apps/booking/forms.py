from django import forms
from django.core.exceptions import ValidationError

from apps.cinema import models as CinemaModels
from apps.slot import models as SlotModels

from .models import Booking


class BookingAdminForm(forms.ModelForm):
    """Custom form for admin panel to create bookings and validate entries as they are not yet added in through table of bookings and seats. Referred in `admin.py`"""

    class Meta:
        model = Booking
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """Runs everytime the form is being created"""

        super().__init__(*args, **kwargs)

        # Filters out active seats and sorts them in the form for convenient and error prone selections
        self.fields["seat"].queryset = (
            CinemaModels.Seat.objects.filter(is_active=True)
            .select_related("cinema__city")
            .order_by("seat_row", "seat_number")
        )

        # Optimizes queries for showing slots in admin panel's booking form
        self.fields["slot"].queryset = SlotModels.Slot.objects.select_related(
            "movie", "cinema__city"
        )

    def clean(self):
        """A form based clean method to be used by admin's booking form for seat validation"""

        cleaned_data = super().clean()

        slot = cleaned_data.get("slot")
        seats = cleaned_data.get("seat")

        if not slot or not seats:
            return cleaned_data

        cinema_id = slot.cinema_id

        # Validation: Only allow seats of same cinema as slot's to be selected
        if any(seat.cinema_id != cinema_id for seat in seats):
            raise ValidationError("All seats must belong to the slot's cinema.")

        # Validation: Only allow active seats to be booked despite filtering active seats only from UI
        if any(not seat.is_active for seat in seats):
            raise ValidationError("All selected seats must be active")

        return cleaned_data
