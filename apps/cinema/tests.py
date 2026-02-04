from datetime import timedelta

from django.utils import timezone
from rest_framework import status, test

from apps.cinema.models import Cinema
from apps.core.models import City, Language
from apps.movie.models import Movie
from apps.slot.models import Slot


class TestCinemaViews(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.city = City.objects.create(name="Kanpur")

        cls.movie = Movie.objects.create(
            name="Test Movie",
            duration=timedelta(hours=2),
            release_date=timezone.now().date(),
        )

        cls.language = Language.objects.create(name="English")

        cls.cinema_active = Cinema.objects.create(
            name="INOX",
            address="Z Square",
            city=cls.city,
            rows=5,
            seats_per_row=5,
        )

        Slot.objects.create(
            movie=cls.movie,
            cinema=cls.cinema_active,
            language=cls.language,
            schedule=now + timedelta(days=1),
            end_schedule=(now + timedelta(days=1, hours=2)),
            price=212,
            is_active=True,
        )

        cls.cinema_inactive = Cinema.objects.create(
            name="PVR",
            address="Mall Road",
            city=cls.city,
            rows=5,
            seats_per_row=5,
        )

        Slot.objects.create(
            movie=cls.movie,
            cinema=cls.cinema_inactive,
            language=cls.language,
            schedule=now + timedelta(days=1),
            end_schedule=(now + timedelta(days=1, hours=2)),
            price=212,
            is_active=False,
        )

    # Seat auto-creation

    def test_seats_created_on_cinema_create(self):
        cinema = Cinema.objects.create(
            name="Test",
            address="Addr",
            city=self.city,
            rows=3,
            seats_per_row=4,
        )

        self.assertEqual(cinema.seats.count(), 12)

    def test_seats_updated_when_rows_increase(self):
        cinema = Cinema.objects.create(
            name="Test2",
            address="Addr",
            city=self.city,
            rows=2,
            seats_per_row=2,
        )

        cinema.rows = 3
        cinema.save()

        self.assertEqual(cinema.seats.filter(is_active=True).count(), 6)

    def test_seats_deactivated_when_rows_decrease(self):
        cinema = Cinema.objects.create(
            name="Test3",
            address="Addr",
            city=self.city,
            rows=3,
            seats_per_row=3,
        )

        cinema.rows = 2
        cinema.save()

        self.assertEqual(cinema.seats.filter(is_active=True).count(), 6)

    # List View

    def test_list_returns_only_cinemas_with_active_slots(self):
        res = self.client.get("/api/cinemas/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        names = [c["name"] for c in res.data["results"]]

        self.assertIn("INOX", names)
        self.assertNotIn("PVR", names)

    def test_list_serializer_fields(self):
        res = self.client.get("/api/cinemas/")
        cinema = res.data["results"][0]

        self.assertIn("id", cinema)
        self.assertIn("name", cinema)
        self.assertIn("address", cinema)
        self.assertIn("city", cinema)

    # Searching

    def test_search_by_name(self):
        res = self.client.get("/api/cinemas/?search=INOX")

        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], "INOX")

    # Filters

    def test_filter_by_city(self):
        res = self.client.get(f"/api/cinemas/?city_id={self.city.id}")

        self.assertEqual(len(res.data["results"]), 1)

    # Detail view

    def test_detail_success(self):
        res = self.client.get(f"/api/cinemas/{self.cinema_active.id}/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn("rows", res.data)
        self.assertIn("seats_per_row", res.data)

    def test_detail_not_found_if_no_active_slot(self):
        res = self.client.get(f"/api/cinemas/{self.cinema_inactive.id}/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_invalid_id(self):
        res = self.client.get("/api/cinemas/999/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
