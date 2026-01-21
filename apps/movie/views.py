from django.utils import timezone
from rest_framework import generics

from apps.core import mixins as CoreMixins

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieDetailsSerializer, MovieListSerializer


class MovieBaseMixin(CoreMixins.UpcomingSlotsQuerySetMixin):
    queryset = Movie.objects.all()
    prefetch_related_args = ("genre", "language")


class MovieListView(MovieBaseMixin, CoreMixins.ListConfigMixin):
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
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.base_queryset(now)


class MovieDetailsView(
    MovieBaseMixin, CoreMixins.UpcomingSlotsPrefetchMixin, generics.RetrieveAPIView
):
    """
    View for movie details that:
    - retrieves all information that was present in movie list details
    - additionally adds description and slots for that movie
    - fetches slots for current movie
    """

    serializer_class = MovieDetailsSerializer

    def get_queryset(self):
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.slots_prefetch_queryset(self.base_queryset(now), now)
