import django_filters

from apps.core import filters as CoreFilters

from .models import Slot


class SlotFilter(django_filters.FilterSet):
    """
    Filter set for slot list view which contains:
    - **language**: multiple strings and comma separated
    - **city**: multiple strings and comma separated
    - **cinema_id**: multiple ids(numbers) and comma separated
    - **movie_id**: multiple ids(numbers) and comma separated
    - **date**: equal to entered date
    """

    language = CoreFilters.CharInFilter(
        field_name="language__name", lookup_expr="in", distinct=True
    )
    city = CoreFilters.CharInFilter(
        field_name="cinema__city__name", lookup_expr="in", distinct=True
    )
    cinema_id = CoreFilters.NumberInFilter(
        field_name="cinema", lookup_expr="in", distinct=True
    )
    movie_id = CoreFilters.NumberInFilter(
        field_name="movie", lookup_expr="in", distinct=True
    )
    date = django_filters.DateTimeFilter(field_name="schedule", lookup_expr="date")

    class Meta:
        model = Slot
        fields = [
            "language",
            "cinema_id",
            "city",
            "movie_id",
            "date",
        ]
