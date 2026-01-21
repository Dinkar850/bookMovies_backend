from django.utils import timezone
from rest_framework import generics

from apps.core import mixins as CoreMixins

from .filters import CinemaFilter
from .models import Cinema
from .serializers import CinemaDetailsSerializer, CinemaListSerializer


class CinemaBaseMixin(CoreMixins.UpcomingSlotsQuerySetMixin):
    """Sets base queryset for returning cinemas"""

    queryset = Cinema.objects.all()
    prefetch_related_args = ["city"]


class CinemaListView(CinemaBaseMixin, CoreMixins.ListConfigMixin):
    """
    View for cinema lists that:
    - filters on city
    - enables search on cinem's name
    - only retrieves cinemas which have active slots
    """

    serializer_class = CinemaListSerializer
    filterset_class = CinemaFilter
    search_fields = ["name"]

    def get_queryset(self):
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.base_queryset(now)


class CinemaDetailsView(
    CinemaBaseMixin, CoreMixins.UpcomingSlotsPrefetchMixin, generics.RetrieveAPIView
):
    """
    View for cinema details that:
    - retrieves all information that was present in cinema list details
    - additionally adds row_seats, seats_per_row and slots for that cinema
    - fetches slots for current cinema
    """

    serializer_class = CinemaDetailsSerializer

    def get_queryset(self):
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.slots_prefetch_queryset(self.base_queryset(now), now)
