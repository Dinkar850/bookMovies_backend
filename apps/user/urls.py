from django.urls import path

from .views import LoginView, RegisterView, TokenRefreshView, UserView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("user/", UserView.as_view(), name="user"),
]
