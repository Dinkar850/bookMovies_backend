from django.utils import timezone
from rest_framework import generics

from apps.core import mixins as CoreMixins
from apps.core import views as CoreViews

from .filters import CinemaFilter
from .models import Cinema
from .serializers import CinemaDetailsSerializer, CinemaListSerializer


class CinemaBaseMixin(CoreMixins.UpcomingSlotsQuerySetMixin):
    """Sets base queryset for returning cinemas having at least one active slot"""

    queryset = Cinema.objects.all()
    prefetch_related_args = ["city"]


class CinemaListView(CinemaBaseMixin, CoreViews.ListView):
    """
    View for cinema lists that:
    - filters on city
    - enables search on cinem's name
    - paginated and ordered on `created_at`
    - only retrieves cinemas which have at least one active slots
    """

    serializer_class = CinemaListSerializer
    filterset_class = CinemaFilter
    search_fields = ["name"]

    def get_queryset(self):
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.base_queryset(now)


class CinemaDetailsView(CinemaBaseMixin, generics.RetrieveAPIView):
    """
    View for cinema details that:
    - retrieves all information that was present in cinema list details
    - additionally adds `rows` and `seats_per_row`
    """

    serializer_class = CinemaDetailsSerializer

    def get_queryset(self):
        """Custom query setter which sets now to the time of calling of request"""

        now = timezone.now()
        return self.base_queryset(now)
