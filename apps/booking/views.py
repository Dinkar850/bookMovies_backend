from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    response,
    status,
    viewsets,
)

from apps.core import pagination as CorePagination

from .filters import BookingFilter
from .models import Booking
from .serializers import (
    BookingCreateRequestSerializer,
    BookingCreateResponseSerializer,
    BookingListSerializer,
)


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Viewset for booking, handles list(paginated and filtered), retrieve, create and cancel specific booking using `detail=True`"""

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CorePagination.BaseCursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related(
                "slot__movie",
                "slot__cinema__city",
                "slot__language",
            )
            .prefetch_related("seat")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateRequestSerializer
        return BookingListSerializer

    def create(self, request, *args, **kwargs):
        """Creates new booking, takes in request through `BookingCreateRequestSerializer` and gives response through `BookingCreateResponseSerializer`"""

        req_serializer = self.get_serializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        booking = req_serializer.save()

        res_serializer = BookingCreateResponseSerializer(
            booking, context=self.get_serializer_context()
        )
        return response.Response(
            {"detail": "Booking created successfully", **res_serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @decorators.action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancels booking through route: `/bookings/:id/cancel`"""

        booking = self.get_object()

        # Checks if booking was already cancelled
        if booking.status == Booking.BookingStatus.CANCELLED:
            raise exceptions.ValidationError(
                {"detail": "Requested booking is already cancelled."}
            )

        # Checks if booking belongs to an expired slot
        if booking.slot.schedule <= timezone.now():
            raise exceptions.ValidationError(
                {"detail": "Cannot cancel a booking after its slot has expired."}
            )

        booking.status = Booking.BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return response.Response(
            {"detail": "Booking cancelled successfully"}, status=status.HTTP_200_OK
        )
