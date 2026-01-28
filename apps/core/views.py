from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from .models import City, Genre, Language
from .pagination import BaseCursorPagination
from .serializers import CitySerializer, GenreSerializer, LanguageSerializer


class ListView(generics.ListAPIView):
    """Base list api view for attaching pagination classes and filter backends"""

    pagination_class = BaseCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]


class GenreListView(ListView):
    """View that returns a list of all genres"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageListView(ListView):
    """View that returns a list of all languages"""

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class CityListView(ListView):
    """View that returns a list of all cities"""

    queryset = City.objects.all()
    serializer_class = CitySerializer
