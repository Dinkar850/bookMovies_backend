from rest_framework import status, test

from apps.core.models import City, Genre, Language


class BaseCoreAPITest(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city1 = City.objects.create(name="Kanpur")
        cls.city2 = City.objects.create(name="Delhi")

        cls.lang1 = Language.objects.create(name="English")
        cls.lang2 = Language.objects.create(name="Hindi")

        cls.genre1 = Genre.objects.create(name="Action")
        cls.genre2 = Genre.objects.create(name="Drama")


class TestCityAPI(BaseCoreAPITest):
    def test_list_cities(self):
        res = self.client.get("/api/filters/cities/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data), 2)


class TestLanguageAPI(BaseCoreAPITest):
    def test_list_languages(self):
        res = self.client.get("/api/filters/languages/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data), 2)


class TestGenreAPI(BaseCoreAPITest):
    def test_list_genres(self):
        res = self.client.get("/api/filters/genres/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data), 2)
