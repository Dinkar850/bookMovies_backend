import django_filters

from apps.core.filters import CharInFilter

from .models import Cinema


class CinemaFilter(django_filters.FilterSet):
    """
    Filter set for cinema list view which contains:
    - **city**: filter based on multiple cities
    """

    city = CharInFilter(field_name="city__name", lookup_expr="in", distinct=True)

    class Meta:
        model = Cinema
        fields = ["city"]
