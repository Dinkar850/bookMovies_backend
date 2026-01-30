from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, permissions, response, status
from rest_framework_simplejwt import tokens, views

from .serializers import TokenObtainPairSerializer, UserSerializer, UserUpdateSerializer


def set_refresh_cookie(res, refresh_token):
    """
    Sets refresh token cookie with max_age derived from SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    """

    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())

    # Checks for production mode to enable cross origin security accordingly
    is_prod = not settings.DEBUG

    res.set_cookie(
        key="refresh",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="None" if is_prod else "Lax",
        path="/api/auth",
        max_age=max_age,
    )


def clear_refresh_cookie(res):
    """Clears refresh cookie from response"""
    is_prod = not settings.DEBUG

    res.delete_cookie(
        key="refresh",
        samesite="None" if is_prod else "Lax",
        path="/api/auth",
    )


class RegisterView(generics.CreateAPIView):
    """
    Registers new user plus:
    - Attaches refresh token in HttpOnly cookie for web
    - Returns access token for registered user in body
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = tokens.RefreshToken.for_user(user)
        access = str(refresh.access_token)

        res = response.Response({"access": access}, status=status.HTTP_201_CREATED)

        set_refresh_cookie(res, str(refresh))
        return res


class LoginView(views.TokenObtainPairView):
    """
    Overrides SimpleJWT default:
    - sets refresh token in HttpOnly cookie for web
    - returns access token in res body
    """

    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)

        if res.status_code != status.HTTP_200_OK:
            return res

        refresh = res.data.pop("refresh")
        access = res.data.get("access")

        if not refresh or not access:
            return res

        res = response.Response({"access": access}, status=status.HTTP_200_OK)
        set_refresh_cookie(res, refresh)
        return res


class UserView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for User model that:
    - **[GET]**: returns all user details after verifying ID from received access token
    - **[PATCH]**: updates user information (phone_number, first_name, last_name)
    - **[DELETE]**: sets user's active state to false
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    http_method_names = ("get", "patch", "delete")

    def get_object(self):
        """Retrieves currently logged in user from ID"""

        return self.request.user

    def get_serializer_class(self):
        """Sets serializer with reference to used method"""

        if self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """Responsible for clearing response cookie and deactivating user by setting `is_active` as false"""

        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])

        res = response.Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(res)
        return res


@method_decorator(csrf_protect, name="dispatch")
class TokenRefreshView(views.TokenRefreshView):
    """Custom `TokenRefreshView` that overrides post mixin for accessing refresh token from cookie instead of accessing from body"""

    def post(self, request, *args, **kwargs):
        """Overrides post mixin for getting refresh token from cookies"""
        refresh = request.COOKIES.get("refresh")

        if not refresh:
            return response.Response(
                {"detail": "Missing or invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # For cases when request.data is immutable
        data = request.data.copy()
        data["refresh"] = refresh

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return response.Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )
