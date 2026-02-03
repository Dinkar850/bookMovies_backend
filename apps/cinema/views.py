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
    GET /api/cinemas/

    Description:
        - Returns list of cinemas having active slots
        - Supports filtering by city
        - Supports search by cinema name
        - Cursor paginated

    Query Params:
        city_id:int
        search:string

    Response:
        200 OK
        [
            {
                "id": int,
                "name": string,
                "address": string,
                "city": string
            }
        ]
    """

    serializer_class = CinemaListSerializer
    filterset_class = CinemaFilter
    search_fields = ("name",)

    def get_queryset(self):
        """Generates queryset from base mixin to be used by this view"""

        return self.base_queryset()


class CinemaDetailsView(CinemaBaseMixin, generics.RetrieveAPIView):
    """
    GET /api/cinemas/{id}/

    Description:
        - Returns detailed information for a single cinema
        - Cinema must have at least one active slot

    Response:
        200 OK
        {
            "id": int,
            "name": string,
            "address": string,
            "city": string,
            "rows": int,
            "seats_per_row": int
        }

    Errors:
        404 Not Found:
            - Cinema not found
    """

    serializer_class = CinemaDetailsSerializer

    def get_queryset(self):
        """Generates queryset from base mixin to be used by this view"""

        return self.base_queryset()
