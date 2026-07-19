from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.cinema.views import CinemaViewset

router = DefaultRouter()
router.register(r"cinemas", CinemaViewset, basename="cinemas")

urlpatterns = [
    path("", include(router.urls)),
]
