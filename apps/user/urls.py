from django.urls import path

from .views import LoginView, RegisterView, TokenRefreshView, UserView

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("auth/token/refresh", TokenRefreshView.as_view()),
    path("user", UserView.as_view()),
]
