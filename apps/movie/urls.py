from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewset

router = DefaultRouter()
router.register(r"movies", MovieViewset, basename="movies")

urlpatterns = [
    path("", include(router.urls)),
]
