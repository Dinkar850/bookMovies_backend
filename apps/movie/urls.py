from django.urls import path

from .views import MovieDetailsView, MovieListView

urlpatterns = [
    path("movies", MovieListView.as_view()),
    path("movies/<int:pk>", MovieDetailsView.as_view()),
]
