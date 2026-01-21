import django_filters

from .models import Movie


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class MovieFilter(django_filters.FilterSet):
    """
    Filter set for movie list view which contains:
    - **genre**: multiple strings and comma separated
    - **language**: multiple strings and comma separated
    - **cinema_id**: multiple ids(numbers) and comma separated
    - **release_date**: greater than or equal to entered date
    """

    genre = CharInFilter(field_name="genre__name", lookup_expr="in", distinct=True)
    language = CharInFilter(
        field_name="language__name", lookup_expr="in", distinct=True
    )
    cinema_id = NumberInFilter(
        field_name="slots__cinema_id", lookup_expr="in", distinct=True
    )
    release_date = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )

    class Meta:
        model = Movie
        fields = ["genre", "language", "cinema_id", "release_date"]
