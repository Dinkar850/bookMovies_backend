import django_filters

from .models import Slot


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class SlotFilter(django_filters.FilterSet):
    """
    Filter set for slot list view which contains:
    - **language**: multiple strings and comma separated
    - **city**: multiple strings and comma separated
    - **cinema_id**: multiple ids(numbers) and comma separated
    - **movie_id**: multiple ids(numbers) and comma separated
    - **date_time**: equal to entered date
    """

    language = CharInFilter(
        field_name="language__name", lookup_expr="in", distinct=True
    )
    city = CharInFilter(
        field_name="cinema__city__name", lookup_expr="in", distinct=True
    )
    cinema_id = NumberInFilter(field_name="cinema", lookup_expr="in", distinct=True)
    movie_id = NumberInFilter(field_name="movie", lookup_expr="in", distinct=True)
    date = django_filters.DateTimeFilter(field_name="date_time", lookup_expr="date")

    class Meta:
        model = Slot
        fields = [
            "language",
            "cinema_id",
            "city",
            "movie_id",
            "date",
        ]
