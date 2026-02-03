from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from .models import City, Genre, Language
from .pagination import BaseCursorPagination
from .serializers import CitySerializer, GenreSerializer, LanguageSerializer


class ListView(generics.ListAPIView):
    """Base list api view for attaching pagination class as `BaseCursorPagination`, filter backends and search support"""

    pagination_class = BaseCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]


class GenreListView(ListView):
    """
    GET /api/filters/genres/

    Description:
        - Returns list of all genres

    Response:
        200 OK
        [
            {
                "id": int,
                "name": string
            }
        ]
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageListView(ListView):
    """
    GET /api/filters/languages/

    Description:
        - Returns list of all languages

    Response:
        200 OK
        [
            {
                "id": int,
                "name": string
            }
        ]
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class CityListView(ListView):
    """
    GET /api/filters/cities/

    Description:
        - Returns list of all cities

    Response:
        200 OK
        [
            {
                "id": int,
                "name": string
            }
        ]
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
