from django.utils import timezone
from rest_framework import generics

from apps.core import views as CoreViews

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieDetailsSerializer, MovieListSerializer


class MovieBaseMixin:
    """Sets base queryset to be used by all views"""

    def base_queryset(self):
        """Generates a queryset for retrieving movie entries having at least one active slot"""

        now = timezone.now()

        return (
            Movie.objects.filter(slots__is_active=True, slots__schedule__gte=now)
            .distinct()
            .prefetch_related("genre", "language")
        )


class MovieListView(MovieBaseMixin, CoreViews.ListView):
    """
    View for movie lists that:
    - filters on cinema_id, genre, language, release_date
    - enables search on movie's name
    - only retrieves movies which have active slots
    """

    serializer_class = MovieListSerializer
    filterset_class = MovieFilter
    search_fields = ["name"]

    def get_queryset(self):
        return self.base_queryset()


class MovieDetailsView(MovieBaseMixin, generics.RetrieveAPIView):
    """View for movie details that retrieves all information that was present in movie list details for a movie that has at least one active slot"""

    serializer_class = MovieDetailsSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return self.base_queryset()
