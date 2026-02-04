from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status, test

from apps.cinema.models import Cinema
from apps.core.models import City, Language
from apps.movie.models import Movie
from apps.slot.models import Slot


class SlotBaseTest(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()

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

    def create_slot(self, start, duration_hours=2):
        end = start + timedelta(hours=duration_hours)

        return Slot(
            schedule=start,
            end_schedule=end,
            price=212,
            movie=self.movie,
            cinema=self.cinema,
            language=self.language,
        )


class TestSlotModelValidation(SlotBaseTest):
    # Model validations

    def test_valid_slot(self):
        slot = self.create_slot(self.now + timedelta(hours=1))
        slot.full_clean()

    def test_past_schedule_invalid(self):
        slot = self.create_slot(self.now - timedelta(hours=1))

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_end_before_start_invalid(self):
        start = self.now + timedelta(hours=2)

        slot = Slot(
            schedule=start,
            end_schedule=(start - timedelta(hours=1)),
            price=212,
            movie=self.movie,
            cinema=self.cinema,
            language=self.language,
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_duration_shorter_than_movie_invalid(self):
        slot = self.create_slot(self.now + timedelta(hours=1), duration_hours=1)

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_before_release_date_invalid(self):
        self.movie.release_date = timezone.localdate(self.now + timedelta(days=2))
        self.movie.save()

        slot = self.create_slot(self.now + timedelta(hours=1))

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_language_not_in_movie_invalid(self):
        other = Language.objects.create(name="Hindi")

        slot = Slot(
            schedule=self.now + timedelta(hours=1),
            end_schedule=(self.now + timedelta(hours=3)),
            price=212,
            movie=self.movie,
            cinema=self.cinema,
            language=other,
        )

        with self.assertRaises(ValidationError):
            slot.full_clean()

    def test_overlap_previous_invalid(self):
        first = self.create_slot(self.now + timedelta(hours=1))
        first.full_clean()
        first.save()

        overlap = self.create_slot(self.now + timedelta(hours=2))

        with self.assertRaises(ValidationError):
            overlap.full_clean()

    def test_adjacent_slot_allowed(self):
        first = self.create_slot(self.now + timedelta(hours=1))
        first.full_clean()
        first.save()

        second = self.create_slot(self.now + timedelta(hours=3))
        second.full_clean()


class TestSlotAPI(SlotBaseTest):
    # API Tests

    def setUp(self):
        self.slot = Slot.objects.create(
            schedule=self.now + timedelta(hours=1),
            end_schedule=(self.now + timedelta(hours=3)),
            price=212,
            movie=self.movie,
            cinema=self.cinema,
            language=self.language,
        )

    # List View

    def test_list_returns_active_future_slots(self):
        res = self.client.get("/api/slots/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_filter_by_language(self):
        res = self.client.get(f"/api/slots/?language={self.language.id}")
        self.assertEqual(len(res.data), 1)

    def test_filter_by_city(self):
        res = self.client.get(f"/api/slots/?city={self.city.id}")

        self.assertEqual(len(res.data), 1)

    def test_filter_by_cinema(self):
        res = self.client.get(f"/api/slots/?cinema_id={self.cinema.id}")

        self.assertEqual(len(res.data), 1)

    def test_filter_by_movie(self):
        res = self.client.get(f"/api/slots/?movie_id={self.movie.id}")

        self.assertEqual(len(res.data), 1)

    def test_filter_by_date(self):
        date = self.slot.schedule.date()

        res = self.client.get(f"/api/slots/?date={date}")

        self.assertEqual(len(res.data), 1)

    # Detail View

    def test_detail_returns_seats(self):
        res = self.client.get(f"/api/slots/{self.slot.id}/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("active_seats", res.data)
        self.assertIn("booked_seats", res.data)

    def test_invalid_slot_returns_404(self):
        res = self.client.get("/api/slots/999/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
