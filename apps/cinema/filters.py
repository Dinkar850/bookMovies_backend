import django_filters

from apps.core.filters import NumberInFilter

from .models import Cinema


class CinemaFilter(django_filters.FilterSet):
    """
    Filter set for cinema list view which contains:
    - **city_id**: multiple comma separated city IDs(integers)
    """

    city_id = NumberInFilter(field_name="city__id", lookup_expr="in", distinct=True)

    class Meta:
        model = Cinema
        fields = ["city"]
