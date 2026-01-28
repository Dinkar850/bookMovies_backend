from rest_framework import generics

from apps.core import mixins as CoreMixins
from apps.core import views as CoreViews

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieDetailsSerializer, MovieListSerializer


class MovieBaseMixin(CoreMixins.UpcomingSlotsQuerySetMixin):
    """Sets base queryset to all movies for returning movies that contain a slot"""

    queryset = Movie.objects.all()
    prefetch_related_args = ("genre", "language")


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
