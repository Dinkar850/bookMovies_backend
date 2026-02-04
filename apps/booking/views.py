from django.utils import timezone
from rest_framework import (
    decorators,
    exceptions,
    permissions,
    response,
    status,
)

from apps.core.viewsets import ModelViewset

from .constants import BookingErrors, BookingMessages
from .filters import BookingFilter
from .models import Booking
from .serializers import (
    BookingCreateRequestSerializer,
    BookingCreateResponseSerializer,
    BookingListSerializer,
)


class BookingViewSet(ModelViewset):
    """
    Endpoints for managing user bookings

    Permissions:
        - IsAuthenticated

    Allowed Methods:
        GET, POST, PATCH


    LIST:
    GET /api/bookings/

    Description:
        - Returns booking history of current user
        - Supports filtering using BookingFilter
        - Cursor paginated

    Query Params:
        booking_status: "B" | "P" | "C"
        booking_period: "upcoming" | "past"
        booking_date:date
        cinema_id:int
        movie_id:int
        slot_id:int
        city_id:int
        language_id:int

    Response:
        200 OK
        "next: null,
        "previous": null,
        "results": [
            {
                "id": int,
                "created_at": datetime,
                "status": string,
                "total_price": decimal,
                "seat_count": int,
                "seats": [
                    {
                        "id": int,
                        "seat_row": int,
                        "seat_number": int
                    }
                ],
                "slot": {
                    "id": int,
                    "schedule": datetime,
                    "price": decimal,
                    "language": string,
                    "movie": {
                        "id": int,
                        "name": string
                    },
                    "cinema": {
                        "id": int,
                        "name": string,
                        "address": string,
                        "city": string
                    }
                }
            }
        ]

    Errors:
        401 Unauthorized:
            - Authentication credentials not provided
            - Invalid or expired token


    CREATE:
    POST /api/bookings/

    Description:
        - Creates new booking for selected slot and seats

    Request Body:
        {
            "slot": int,
            "seats": [int]
        }

    Response:
        201 Created
        {
            "detail": "Booking created successfully",
            "id": int,
            "created_at": datetime,
            "status": string,
            "total_price": decimal,
            "seat_count": int,
            "seats": [
                {
                    "id": int,
                    "seat_row": int,
                    "seat_number": int
                }
            ]
        }

    Errors:
        400 Bad Request:
            - Validation errors
            - Seats already booked
            - Invalid cinema seats
            - Seat limit exceeded
        401 Unauthorized:
            - Authentication credentials not provided
            - Invalid or expired token


    CANCEL:
    PATCH /api/bookings/{id}/cancel/

    Description:
        - Cancels existing booking by updating status to cancelled

    Response:
        200 OK
        {
            "detail": "Booking cancelled successfully"
        }

    Errors:
        400 Bad Request:
            - Already cancelled
            - Slot expired
        401 Unauthorized:
            - Authentication credentials not provided
            - Invalid or expired token
        404 Not Found:
            - Booking not found
    """

    permission_classes = [permissions.IsAuthenticated]
    filterset_class = BookingFilter

    def get_queryset(self):
        """Uses custom queryset for optimizations with this view"""

        return (
            Booking.objects.filter(user=self.request.user)
            .select_related(
                "slot__movie",
                "slot__cinema__city",
                "slot__language",
            )
            .prefetch_related("seats")
        )

    def get_serializer_class(self):
        """
        Sets serializer with the following conditions:
        - Uses `BookingCreateRequestSerializer` when action is create
        - Otherwise uses `BookingListSerializer`
        """

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
            {"detail": BookingMessages.CREATED, **res_serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @decorators.action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        Cancels booking with the following checks:
        - Booking is not already cancelled
        - Booking's slot has not expired
        """

        booking = self.get_object()

        # Checks if booking was already cancelled
        if booking.status == Booking.BookingStatus.CANCELLED:
            raise exceptions.ValidationError(
                {"detail": BookingErrors.ALREADY_CANCELLED}
            )

        # Checks if booking belongs to an expired slot
        if booking.slot.schedule <= timezone.now():
            raise exceptions.ValidationError({"detail": BookingErrors.EXPIRED_SLOT})

        booking.status = Booking.BookingStatus.CANCELLED
        booking.save(update_fields=("status", "updated_at"))

        return response.Response(
            {"detail": BookingMessages.CANCELLED}, status=status.HTTP_200_OK
        )
