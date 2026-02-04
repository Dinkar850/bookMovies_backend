import django_filters
from django.utils import timezone

from apps.booking.models import Booking
from apps.core.filters import NumberInFilter


class BookingFilter(django_filters.FilterSet):
    """
    Filterset for bookings that contain
    - **booking_status**: status of booking ("B: Booked", "P: Pending". "C": Cancelled)
    - **booking_period**: `past` for past bookings (compared using slot's schedule) and `upcoming` for current and future
    - **booking_date**: date of slot for which booking was made
    - **movie_id**: multiple comma separated movie id's
    - **cinema_id**: multiple comma separated cinema id's
    - **slot_id**: multiple comma separated slot id's
    - **city_id**: multiple comma separated city id's
    - **language_id**: multiple comma separated language id's
    """

    booking_status = django_filters.ChoiceFilter(
        field_name="status", choices=Booking.BookingStatus.choices
    )
    booking_period = django_filters.ChoiceFilter(
        field_name="slot__schedule",
        choices=(("upcoming", "upcoming"), ("past", "past")),
        method="filter_status",
    )

    booking_date = django_filters.DateTimeFilter(
        field_name="slot__schedule", lookup_expr="date"
    )
    cinema_id = NumberInFilter(
        field_name="slot__cinema", lookup_expr="in", distinct=True
    )
    movie_id = NumberInFilter(field_name="slot__movie", lookup_expr="in", distinct=True)
    slot_id = NumberInFilter(field_name="slot", lookup_expr="in", distinct=True)
    city_id = NumberInFilter(
        field_name="slot__cinema__city", lookup_expr="in", distinct=True
    )
    language_id = NumberInFilter(
        field_name="slot__language", lookup_expr="in", distinct=True
    )

    class Meta:
        model = Booking
        fields = [
            "booking_status",
            "booking_period",
            "booking_date",
            "cinema_id",
            "movie_id",
            "slot_id",
            "city_id",
            "language_id",
        ]

    def filter_status(self, qs, name, value):
        """
        Filters parent queryset based on status:
        - `upcoming`: currently active bookings
        - `past`: past bookings
        """

        now = timezone.now()

        if value == "upcoming":
            return qs.filter(slot__schedule__gte=now)

        if value == "past":
            return qs.filter(slot__schedule__lt=now)

        return qs
