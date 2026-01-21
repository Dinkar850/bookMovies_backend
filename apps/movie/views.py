from django.db.models import Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from apps.core import pagination as CorePagination
from apps.slot import models as SlotModels

from .filters import MovieFilter
from .models import Movie
from .serializers import MovieDetailsSerializer, MovieListSerializer


class BaseQuerySetMixin:
    """Generates common queryset for `MovieListView` and `MovieDetailsView`"""

    def base_queryset(self, now):
        return (
            Movie.objects.filter(slots__is_active=True, slots__date_time__gte=now)
            .distinct()
            .prefetch_related("genre", "language")
        )


class MovieListView(BaseQuerySetMixin, generics.ListAPIView):
    """
    View for movie lists that:
    - filters on cinema_id, genre, language, release_date
    - enables search on movie's name
    - paginates and orders itself by pagination class on `created_at` and `id`
    - only retrieves movies which have active slots
    """

    serializer_class = MovieListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = MovieFilter
    pagination_class = CorePagination.BaseCursorPagination
    search_fields = ["name"]

    def get_queryset(self):
        """Custom query setter which sets now to calling of request"""

        now = timezone.now()
        return self.base_queryset(now)


class MovieDetailsView(BaseQuerySetMixin, generics.RetrieveAPIView):
    """
    View for movie details that:
    - retrieves all information that was present in movie list details
    - additionally adds description and slots
    - fetches slots for current movie
    """

    serializer_class = MovieDetailsSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Custom query setter which sets now to calling of request"""

        now = timezone.now()
        return self.base_queryset(now).prefetch_related(
            Prefetch(
                "slots",
                queryset=SlotModels.Slot.objects.filter(
                    is_active=True,
                    date_time__gte=now,
                )
                .select_related("movie", "cinema", "language")
                .order_by("date_time"),
                to_attr="active_slots",
            )
        )
