from django.utils import timezone

from apps.core.viewsets import ReadOnlyModelViewset

from .filters import CinemaFilter
from .models import Cinema
from .serializers import CinemaDetailsSerializer, CinemaListSerializer


class CinemaViewset(ReadOnlyModelViewset):
    """
    Endpoint for browsing cinemas

    Permissions:
        - AllowAny

    Allowed Methods:
        GET

    LIST
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
        "next": null,
        "previous": null,
        "results": [
            {
                "id": int,
                "name": string,
                "address": string,
                "city": string
            }
        ]

    RETRIEVE
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

    filterset_class = CinemaFilter

    def get_queryset(self):
        """
        - Sets now to current date and time
        - Generates a queryset for retrieving movie entries having at least one active slot
        """

        now = timezone.now()

        return (
            Cinema.objects.filter(slots__is_active=True, slots__schedule__gte=now)
            .distinct()
            .select_related("city")
        )

    def get_serializer_class(self):
        """
        Sets serializer with the following conditions:
        - Uses `CinemaListSerializer` when action is `list()`
        - Otherwise uses `CinemaDetailsSerializer`
        """

        if self.action == "list":
            return CinemaListSerializer

        return CinemaDetailsSerializer
