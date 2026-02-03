from django.urls import path

from .views import SlotDetailsView, SlotListView

urlpatterns = [
    path("", SlotListView.as_view(), name="slots"),
    path("<int:pk>/", SlotDetailsView.as_view(), name="slot"),
]
