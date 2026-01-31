from django.utils import timezone
from rest_framework import generics

from apps.core import views as CoreViews

from .filters import CinemaFilter
from .models import Cinema
from .serializers import CinemaDetailsSerializer, CinemaListSerializer


class CinemaBaseMixin:
    """Sets base queryset to be used by all views"""

    def base_queryset(self):
        """Generates a queryset for retrieving cinema entries having at least one active slot"""

        now = timezone.now()

        return (
            Cinema.objects.filter(slots__is_active=True, slots__schedule__gte=now)
            .distinct()
            .select_related("city")
        )


class CinemaListView(CinemaBaseMixin, CoreViews.ListView):
    """
    View for cinema lists that:
    - filters on city
    - enables search on cinema's name
    - paginated and ordered on `created_at`
    - only retrieves cinemas which have at least one active slots
    """

    serializer_class = CinemaListSerializer
    filterset_class = CinemaFilter
    search_fields = ["name"]

    def get_queryset(self):
        return self.base_queryset()


class CinemaDetailsView(CinemaBaseMixin, generics.RetrieveAPIView):
    """
    View for cinema details that:
    - retrieves all information that was present in cinema list details
    - additionally adds `rows` and `seats_per_row`
    """

    serializer_class = CinemaDetailsSerializer

    def get_queryset(self):
        return self.base_queryset()
