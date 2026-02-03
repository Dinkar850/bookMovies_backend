from django.urls import path

from .views import CinemaDetailsView, CinemaListView

urlpatterns = [
    path("", CinemaListView.as_view(), name="cinemas"),
    path("<int:pk>/", CinemaDetailsView.as_view(), name="cinema"),
]
