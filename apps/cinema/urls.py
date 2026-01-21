from django.urls import path

from .views import CinemaDetailsView, CinemaListView

urlpatterns = [
    path("", CinemaListView.as_view()),
    path("<int:pk>", CinemaDetailsView.as_view()),
]
