from django.urls import path

from apps.core.views import CityListView, GenreListView, LanguageListView

urlpatterns = [
    path("filters/genres/", GenreListView.as_view(), name="genres"),
    path("filters/cities/", CityListView.as_view(), name="cities"),
    path("filters/languages/", LanguageListView.as_view(), name="languages"),
]
