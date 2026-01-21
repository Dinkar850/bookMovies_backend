from rest_framework import generics

from .models import City, Genre, Language
from .serializers import CitySerializer, GenreSerializer, LanguageSerializer


class GenreListView(generics.ListAPIView):
    """View that returns a list of all genres"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageListView(generics.ListAPIView):
    """View that returns a list of all languages"""

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class CityListView(generics.ListAPIView):
    """View that returns a list of all cities"""

    queryset = City.objects.all()
    serializer_class = CitySerializer
