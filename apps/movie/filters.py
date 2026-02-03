import django_filters

from apps.core.filters import NumberInFilter

from .models import Movie


class MovieFilter(django_filters.FilterSet):
    """
    Filterset for movie list view which contains:
    - **genre_id**: multiple IDs(integers) and comma separated
    - **language_id**: multiple IDs(integers) and comma separated
    - **cinema_id**: multiple IDs(integers) and comma separated
    - **release_date**: greater than or equal to entered date
    """

    genre_id = NumberInFilter(field_name="genres__id", lookup_expr="in", distinct=True)
    language_id = NumberInFilter(
        field_name="languages__id", lookup_expr="in", distinct=True
    )
    cinema_id = NumberInFilter(
        field_name="slots__cinema_id", lookup_expr="in", distinct=True
    )
    release_date = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )

    class Meta:
        model = Movie
        fields = ("genre_id", "language_id", "cinema_id", "release_date")
