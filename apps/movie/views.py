from django.utils import timezone

from apps.core.viewsets import ReadOnlyModelViewset
from apps.movie.filters import MovieFilter
from apps.movie.models import Movie
from apps.movie.serializers import MovieDetailsSerializer, MovieListSerializer


class MovieViewset(ReadOnlyModelViewset):
    """
    Endpoint for browsing movies

    Permissions:
        - AllowAny

    Allowed Methods:
        GET

    LIST
    GET /api/movies/

    Description:
    - Returns list of movies having active slots
    - Supports filtering by cinema, genre, language, release_date
    - Supports search by movie name
    - Cursor paginated

    Query Params:
        cinema_id:int
        genre_id:int
        language_id:int
        release_date:date
        search:string

    Response:
        200 OK
        {
            "next": null,
            "previous": null,
            "results": [
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
        }

    RETRIEVE
    GET /api/movies/{slug}/

    Description:
    - Slug based retrieval
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
    """

    filterset_class = MovieFilter
    lookup_field = "slug"

    def get_queryset(self):
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

    def get_serializer_class(self):
        """
        Sets serializer with the following conditions:
        - Uses `MovieListSerializer` when action is `list()`
        - Otherwise uses `MovieDetailsSerializer`
        """

        if self.action == "list":
            return MovieListSerializer

        return MovieDetailsSerializer
