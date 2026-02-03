from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SlotViewset

router = DefaultRouter()
router.register(r"slots", SlotViewset, basename="slots")

urlpatterns = [
    path("", include(router.urls)),
]
