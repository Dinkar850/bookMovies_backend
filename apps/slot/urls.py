from django.urls import path

from .views import SlotDetailsView, SlotListView

urlpatterns = [
    path("", SlotListView.as_view()),
    path("<int:pk>", SlotDetailsView.as_view()),
]
