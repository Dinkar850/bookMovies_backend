from django.urls import path

from .views import MovieDetailsView, MovieListView

urlpatterns = [
    path("", MovieListView.as_view()),
    path("<int:pk>", MovieDetailsView.as_view()),
]
