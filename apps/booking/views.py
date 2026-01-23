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
from .serializers import BookingCreateSerializer, BookingListSerializer


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
            .select_related("slot__movie", "slot__cinema")
            .prefetch_related("seats")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingListSerializer

    def create(self, request, *args, **kwargs):
        """Creates new booking, takes in request through `BookingCreateSerializer` and gives response through `BookingListSerializer`"""
        req_serializer = self.get_serializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        booking = req_serializer.save()

        res_serializer = BookingListSerializer(
            booking, context=self.get_serializer_context()
        )
        return response.Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancels booking through route: `/bookings/:id/cancel`"""
        booking = self.get_object()

        # Checks if booking was already cancelled
        if booking.status == Booking.BookingStatus.CANCELLED:
            raise exceptions.ValidationError(
                {"detail": "Booking is already cancelled."}
            )

        # Checks if a booking for an already expired slot  is not getting cancelled
        if booking.slot.schedule <= timezone.now():
            raise exceptions.ValidationError(
                {"detail": "Cannot cancel after showtime."}
            )

        booking.status = Booking.BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return response.Response({"status": "cancelled"}, status=status.HTTP_200_OK)
