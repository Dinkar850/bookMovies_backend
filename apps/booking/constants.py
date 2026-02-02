class BookingDefaults:
    MAX_SEATS_PER_BOOKING = 10


class BookingMessages:
    CREATED = "Booking created successfully"
    CANCELLED = "Booking cancelled successfuly"


class BookingErrors:
    ALREADY_CANCELLED = "Booking has been already previously cancelled"
    EXPIRED_SLOT = "Slot associated with the booking has expired"
    DUPLICATE_SEATS = "Duplicate seat(s) found in request"
    EXCEEDED_SEATS_LIMIT = f"More than {BookingDefaults.MAX_SEATS_PER_BOOKING} seats cannot be booked per booking"
    INVALID_CINEMA = "Some or all seats do not belong to the selected slot's cinema"
    SEATS_ALREADY_BOOKED = "Some or all seats for this booking are already booked"
