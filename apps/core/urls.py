from django.urls import path

from .views import CityListView, GenreListView, LanguageListView

urlpatterns = [
    path("genres", GenreListView.as_view()),
    path("cities", CityListView.as_view()),
    path("languages", LanguageListView.as_view()),
]
