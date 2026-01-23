import django_filters
from django.utils import timezone

from apps.core import filters as CoreFilters

from .models import Booking


class BookingFilter(django_filters.FilterSet):
    """
    Filterset for bookings that contain
    - **booking_status**: status of booking ("B: Booked", "P: Pending". "C": Cancelled)
    - **booking_type**: `history` for past bookings and `upcoming` for current and future
    - **booking_date**: date of slot for which booking was made
    - **movie_id**: multiple comma separated movie id's
    - **cinema_id**: multiple comma separated cinema id's
    - **slot_id**: multiple comma separated slot id's
    - **city**: multiple comma separated city names
    - **language**: multiple comma separated language names
    """

    booking_status = django_filters.ChoiceFilter(
        field_name="status", choices=Booking.BookingStatus.choices
    )
    booking_type = django_filters.ChoiceFilter(
        field_name="slot__schedule",
        choices=(("upcoming", "upcoming"), ("history", "history")),
        method="filter_status",
    )

    booking_date = django_filters.DateTimeFilter(
        field_name="slot__schedule", lookup_expr="date"
    )
    cinema_id = CoreFilters.NumberInFilter(
        field_name="slot__cinema", lookup_expr="in", distinct=True
    )
    movie_id = CoreFilters.NumberInFilter(
        field_name="slot__movie", lookup_expr="in", distinct=True
    )
    slot_id = CoreFilters.NumberInFilter(
        field_name="slot", lookup_expr="in", distinct=True
    )
    city = CoreFilters.CharInFilter(
        field_name="slot__cinema__city__name", lookup_expr="in", distinct=True
    )
    language = CoreFilters.CharInFilter(
        field_name="slot__language__name", lookup_expr="in", distinct=True
    )

    class Meta:
        model = Booking
        fields = [
            "booking_status",
            "booking_type",
            "booking_date",
            "cinema_id",
            "movie_id",
            "slot_id",
            "city",
            "language",
        ]

    def filter_status(self, qs, name, value):
        """Filters parent queryset based on status"""

        now = timezone.now()

        if value == "upcoming":
            return qs.filter(slot__schedule__gte=now)

        if value == "history":
            return qs.filter(slot__schedule__lt=now)

        return qs
