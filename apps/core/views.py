from rest_framework import generics

from .models import City, Genre, Language
from .pagination import BaseCursorPagination
from .serializers import CitySerializer, GenreSerializer, LanguageSerializer


class ListView(generics.ListAPIView):
    """Base list api view for attaching pagination class as `BaseCursorPagination`"""

    pagination_class = BaseCursorPagination


class GenreListView(ListView):
    """
    GET /api/filters/genres/

    Description:
        - Returns list of all genres
        - Cursor paginated

    Response:
        200 OK
        {
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": int,
                    "name": string
                }
            ]
        }
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageListView(ListView):
    """
    GET /api/filters/languages/

    Description:
        - Returns list of all languages
        - Cursor paginated

    Response:
        200 OK
        {
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": int,
                    "name": string
                }
            ]
        }
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class CityListView(ListView):
    """
    GET /api/filters/cities/

    Description:
        - Returns list of all cities
        - Cursor paginated

    Response:
        200 OK
        {
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": int,
                    "name": string
                }
            ]
        }
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
