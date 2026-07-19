import django_filters

from apps.core.filters import NumberInFilter
from apps.slot.models import Slot


class SlotFilter(django_filters.FilterSet):
    """
    Filter set for slot list view which contains:
    - **language_id**: multiple strings and comma separated
    - **city_id**: multiple strings and comma separated
    - **cinema_id**: multiple ids(numbers) and comma separated
    - **movie_id**: multiple ids(numbers) and comma separated
    - **date**: equal to entered date
    """

    language_id = NumberInFilter(field_name="language", lookup_expr="in", distinct=True)
    city_id = NumberInFilter(field_name="cinema__city", lookup_expr="in", distinct=True)
    cinema_id = NumberInFilter(field_name="cinema", lookup_expr="in", distinct=True)
    movie_id = NumberInFilter(field_name="movie", lookup_expr="in", distinct=True)
    date = django_filters.DateTimeFilter(field_name="schedule", lookup_expr="date")

    class Meta:
        model = Slot
        fields = (
            "language_id",
            "cinema_id",
            "city_id",
            "movie_id",
            "date",
        )
