from datetime import timedelta

from django.utils import timezone
from rest_framework import status, test

from apps.booking.models import Booking
from apps.cinema.models import Cinema
from apps.core.models import City, Language
from apps.movie.models import Movie
from apps.slot.models import Slot
from apps.user.models import User


class BookingBaseTest(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()

        cls.user = User.objects.create_user(
            email="test@test.com",
            password="pass12345",
            first_name="Test",
            phone_number="9876543210",
        )

        cls.city = City.objects.create(name="Kanpur")

        cls.cinema = Cinema.objects.create(
            name="INOX",
            address="Z Square",
            city=cls.city,
            rows=3,
            seats_per_row=3,
        )

        cls.language = Language.objects.create(name="English")

        cls.movie = Movie.objects.create(
            name="Batman",
            duration=timedelta(hours=2),
            release_date=timezone.localdate(cls.now),
        )
        cls.movie.languages.add(cls.language)

        cls.slot = Slot.objects.create(
            schedule=cls.now + timedelta(hours=1),
            end_time=(cls.now + timedelta(hours=3)).time(),
            price=212,
            movie=cls.movie,
            cinema=cls.cinema,
            language=cls.language,
        )

        cls.seats = list(cls.cinema.seats.filter(is_active=True)[:3])

    def login(self):
        self.client.force_authenticate(self.user)


class TestBookingCreate(BookingBaseTest):
    # Booking Creation

    def setUp(self):
        super().setUp()
        self.login()

    def test_create_success(self):
        data = {
            "slot": self.slot.id,
            "seats": [self.seats[0].id, self.seats[1].id],
        }

        res = self.client.post("/api/bookings/", data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["seat_count"], 2)
        self.assertEqual(res.data["total_price"], 424)
        self.assertEqual(res.data["status"], Booking.BookingStatus.BOOKED)

        self.assertEqual(Booking.objects.count(), 1)

    def test_duplicate_seats_invalid(self):
        data = {
            "slot": self.slot.id,
            "seats": [self.seats[0].id, self.seats[0].id],
        }

        res = self.client.post("/api/bookings/", data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seat_from_other_cinema_invalid(self):
        other = Cinema.objects.create(
            name="Other",
            address="Addr",
            city=self.city,
            rows=2,
            seats_per_row=2,
        )

        seat = other.seats.first()

        data = {
            "slot": self.slot.id,
            "seats": [seat.id],
        }

        res = self.client.post("/api/bookings/", data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_already_booked_seat_invalid(self):
        Booking.objects.create(
            user=self.user,
            slot=self.slot,
            status=Booking.BookingStatus.BOOKED,
        ).seats.set([self.seats[0]])

        data = {
            "slot": self.slot.id,
            "seats": [self.seats[0].id],
        }

        res = self.client.post("/api/bookings/", data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestBookingList(BookingBaseTest):
    # Booking List View

    def setUp(self):
        super().setUp()
        self.login()

        self.booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            status=Booking.BookingStatus.BOOKED,
        )
        self.booking.seats.set(self.seats[:1])

    def test_list_returns_user_bookings_only(self):
        res = self.client.get("/api/bookings/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    # Filtering

    def test_filter_by_status(self):
        res = self.client.get("/api/bookings/?booking_status=B")

        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_by_cinema(self):
        res = self.client.get(f"/api/bookings/?cinema_id={self.cinema.id}")

        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_upcoming(self):
        res = self.client.get("/api/bookings/?booking_type=upcoming")

        self.assertEqual(len(res.data["results"]), 1)


class TestBookingCancel(BookingBaseTest):
    # Booking cancellation

    def setUp(self):
        super().setUp()
        self.login()

        self.booking = Booking.objects.create(
            user=self.user,
            slot=self.slot,
            status=Booking.BookingStatus.BOOKED,
        )

    def test_cancel_success(self):
        res = self.client.patch(f"/api/bookings/{self.booking.id}/cancel/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.BookingStatus.CANCELLED)

    def test_cancel_twice_invalid(self):
        self.booking.status = Booking.BookingStatus.CANCELLED
        self.booking.save()

        res = self.client.patch(f"/api/bookings/{self.booking.id}/cancel/")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_expired_slot_invalid(self):
        self.slot.schedule = timezone.now() - timedelta(hours=1)
        self.slot.save()

        res = self.client.patch(f"/api/bookings/{self.booking.id}/cancel/")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
