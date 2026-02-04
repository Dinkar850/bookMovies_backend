from datetime import timedelta

from django.utils import timezone
from rest_framework import status, test

from apps.cinema.models import Cinema
from apps.core.models import City, Genre, Language
from apps.movie.models import Movie
from apps.slot.models import Slot


class TestMovieViews(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre = Genre.objects.create(name="Action")
        cls.language = Language.objects.create(name="English")
        cls.city = City.objects.create(name="Kanpur")

        cls.cinema = Cinema.objects.create(
            name="INOX",
            address="Z Square",
            rows=5,
            city=cls.city,
            seats_per_row=5,
        )

        cls.movie_active = Movie.objects.create(
            name="Active Movie",
            duration=timedelta(hours=2),
            release_date=timezone.now().date(),
        )
        cls.movie_active.genres.add(cls.genre)
        cls.movie_active.languages.add(cls.language)

        cls.movie_inactive = Movie.objects.create(
            name="Inactive Movie",
            duration=timedelta(hours=2),
            release_date=timezone.now().date(),
        )

        now = timezone.now()

        Slot.objects.create(
            movie=cls.movie_active,
            cinema=cls.cinema,
            language=cls.language,
            schedule=now + timedelta(days=1),
            end_schedule=(now + timedelta(days=1, hours=2)),
            price=212,
            is_active=True,
        )

        Slot.objects.create(
            movie=cls.movie_inactive,
            cinema=cls.cinema,
            language=cls.language,
            schedule=now + timedelta(days=1),
            end_schedule=(now + timedelta(days=1, hours=2)),
            price=212,
            is_active=False,
        )

    # List View

    def test_movie_list_returns_only_active_movies(self):
        res = self.client.get("/api/movies/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        names = [m["name"] for m in res.data["results"]]

        self.assertIn("Active Movie", names)
        self.assertNotIn("Inactive Movie", names)

    def test_movie_list_serializer_fields(self):
        res = self.client.get("/api/movies/")
        movie = res.data["results"][0]

        self.assertIn("id", movie)
        self.assertIn("name", movie)
        self.assertIn("slug", movie)
        self.assertIn("genres", movie)
        self.assertIn("languages", movie)
        self.assertIn("release_date", movie)

    # Searching

    def test_search_movie_by_name(self):
        res = self.client.get("/api/movies/?search=Active")

        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], "Active Movie")

    # Filtering

    def test_filter_by_genre(self):
        res = self.client.get(f"/api/movies/?genre_id={self.genre.id}")

        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_by_language(self):
        res = self.client.get(f"/api/movies/?language_id={self.language.id}")

        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_by_cinema(self):
        res = self.client.get(f"/api/movies/?cinema_id={self.cinema.id}")

        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_by_release_date(self):
        today = timezone.now().date()

        res = self.client.get(f"/api/movies/?release_date={today}")

        self.assertEqual(len(res.data["results"]), 1)

    # Detail View

    def test_movie_detail_success(self):
        slug = self.movie_active.slug

        res = self.client.get(f"/api/movies/{slug}/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Active Movie")
        self.assertIn("description", res.data)

    def test_movie_detail_invalid_slug(self):
        res = self.client.get("/api/movies/does-not-exist/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_movie_detail_not_returned_if_no_active_slot(self):
        slug = self.movie_inactive.slug

        res = self.client.get(f"/api/movies/{slug}/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
