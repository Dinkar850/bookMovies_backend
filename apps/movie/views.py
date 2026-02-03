from django.utils import timezone
from rest_framework import generics

from apps.core import views as CoreViews

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieDetailsSerializer, MovieListSerializer


class MovieBaseMixin:
    """Sets base queryset to be used by all views"""

    def base_queryset(self):
        """
        - Sets now to current date and time
        - Generates a queryset for retrieving movie entries having at least one active slot
        """

        now = timezone.now()

        return (
            Movie.objects.filter(slots__is_active=True, slots__schedule__gte=now)
            .distinct()
            .prefetch_related("genres", "languages")
        )


class MovieListView(MovieBaseMixin, CoreViews.ListView):
    """
    GET /movies/

    Description:
        - Returns list of movies having active slots
        - Supports filtering by cinema, genre, language, release_date
        - Supports search by movie name

    Query Params:
        cinema_id:int
        genre_id:int
        language_id:int
        release_date:date
        search:string

    Response:
        200 OK
        [
            {
                "id": int,
                "name": string,
                "slug": string,
                "genres": [string],
                "languages": [string],
                "cover_image": string,
                "release_date": date
            }
        ]
    """

    serializer_class = MovieListSerializer
    filterset_class = MovieFilter
    search_fields = ("name",)

    def get_queryset(self):
        """Generates queryset from base mixin to be used by this view"""

        return self.base_queryset()


class MovieDetailsView(MovieBaseMixin, generics.RetrieveAPIView):
    """
    GET /movies/{slug}/

    Description:
        - Returns detailed information for a single movie
        - Movie must have at least one active slot

    Response:
        200 OK
        {
            "id": int,
            "name": string,
            "slug": string,
            "genres": [string],
            "languages": [string],
            "cover_image": string,
            "release_date": date,
            "description": string
        }

    Errors:
        404 Not Found:
            - Movie not found
            - No active slots available
    """

    serializer_class = MovieDetailsSerializer
    lookup_field = "slug"

    def get_queryset(self):
        """Generates queryset from base mixin to be used by this view"""

        return self.base_queryset()
