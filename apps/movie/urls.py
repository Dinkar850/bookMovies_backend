from django.urls import path

from .views import MovieDetailsView, MovieListView

urlpatterns = [
    path("", MovieListView.as_view(), name="movies"),
    path("<slug:slug>/", MovieDetailsView.as_view(), name="movie"),
]
