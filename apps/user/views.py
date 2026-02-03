import contextlib

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView
from rest_framework_simplejwt import exceptions, tokens, views

from .constants import UserErrors, UserMessages
from .serializers import TokenObtainPairSerializer, UserSerializer, UserUpdateSerializer


def set_refresh_cookie(res, refresh_token):
    """
    Sets refresh token cookie with `max_age` derived from `SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']`
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
    POST /api/auth/register/

    Description:
        - Creates new user account
        - Generates access token
        - Sets refresh token in HttpOnly cookie

    Permissions:
        - AllowAny

    Response:
        201 Created
        {
            "detail": string,
            "access": string
        }

    Errors:
        400 Bad Request:
            - Validation errors
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        - Creates new user
        - Generates and sets new refresh token in HttpOnly cookie
        - Sets access token in response body
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = tokens.RefreshToken.for_user(user)
        access = str(refresh.access_token)

        res = response.Response(
            {"detail": UserMessages.REGISTERED, "access": access},
            status=status.HTTP_201_CREATED,
        )

        set_refresh_cookie(res, str(refresh))

        return res


class LoginView(views.TokenObtainPairView):
    """
    POST /api/auth/login/

    Description:
        - Authenticates user credentials
        - Returns access token
        - Stores refresh token in HttpOnly cookie

    Permissions:
        - AllowAny

    Response:
        200 OK
        {
            "detail": string,
            "access": string
        }

    Errors:
        401 Unauthorized:
            - Authentication credentials were not provided
            - Invalid or expired token
    """

    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        - Sets refresh token in HttpOnly cookie
        - Returns access token in response body
        """

        res = super().post(request, *args, **kwargs)

        if res.status_code != status.HTTP_200_OK:
            return res

        refresh = res.data.pop("refresh")
        access = res.data.get("access")

        if not refresh or not access:
            return res

        res = response.Response(
            {"detail": UserMessages.LOGGED_IN, "access": access},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(res, refresh)

        return res


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Description:
        - Blacklists current refresh token
        - Clears refresh cookie

    Permissions:
        - IsAuthenticated

    Response:
        200 OK
        {
            "detail": string
        }

    Errors:
        401 Unauthorized:
            - Authentication credentials were not provided
            - Invalid or expired token
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        - Blacklists the previously issues refresh token
        - Clears refresh token from HttpOnly cookie
        """

        refresh = request.COOKIES.get("refresh")

        if refresh:
            with contextlib.suppress(Exception):
                tokens.RefreshToken(refresh).blacklist()

        res = response.Response(
            {"detail": UserMessages.LOGGED_OUT}, status=status.HTTP_200_OK
        )

        clear_refresh_cookie(res)

        return res


class UserView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoints for managing current authenticated user
    - /api/user/

    Permissions:
        - IsAuthenticated

    Allowed Methods:
        GET, PATCH, DELETE


    GET:
        - Returns current user details

        Response:
            200 OK
            {
                "id": int,
                "first_name": string,
                "last_name": string,
                "email": string,
                "phone_number": string
            }


    PATCH:
        - Updates profile fields

        Request Body:
            {
                "first_name": string,
                "last_name": string,
                "phone_number": string
                ...
            }

        Response:
            200 OK
            {
                "first_name": string,
                "last_name": string,
                "phone_number": string
            }


    DELETE:
        - Sets user inactive
        - Blacklists refresh token
        - Clears cookie

        Response:
            204 No Content

    Errors:
        401 Unauthorized:
            - Authentication credentials were not provided
            - Invalid or expired token
    """

    permission_classes = (permissions.IsAuthenticated,)
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
        """
        - Responsible for clearing response cookie and deactivating user by setting `is_active` as false
        - Blacklists refresh token of this user
        - Clears refresh token from HttpOnly cookie
        """

        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])

        refresh = request.COOKIES.get("refresh")

        if refresh:
            with contextlib.suppress(Exception):
                tokens.RefreshToken(refresh).blacklist()

        res = response.Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(res)

        return res


@method_decorator(csrf_protect, name="dispatch")
class TokenRefreshView(views.TokenRefreshView):
    """
    POST /api/auth/token/refresh/

    Description:
        - Reads refresh token from HttpOnly cookie
        - Issues new access token
        - Rotates refresh token
        - Sets new refresh cookie

    Permissions:
        - AllowAny

    Request Body:
        {}

    Response:
        200 OK
        {
            "access": string
        }

    Errors:
        400 Bad Request:
            - Missing refresh token
        401 Unauthorized:
            - Invalid, blacklisted or expired token
    """

    def post(self, request, *args, **kwargs):
        """
        - Overrides post mixin for accessing refresh token from HttpOnly cookie
        - Rotates refresh token, also blacklists previously issued refresh token
        """

        refresh = request.COOKIES.get("refresh")

        if not refresh:
            return response.Response(
                {"detail": UserErrors.INVALID_REFRESH_TOKEN},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # For cases when request.data is immutable
        data = request.data.copy()
        data["refresh"] = refresh

        serializer = self.get_serializer(data=data)

        # Issues error in case of blacklisted refresh token
        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.TokenError:
            return response.Response(
                {"detail": UserErrors.INVALID_REFRESH_TOKEN},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        new_refresh = serializer.validated_data.pop("refresh")

        res = response.Response(serializer.validated_data, status=status.HTTP_200_OK)

        if new_refresh:
            set_refresh_cookie(res, new_refresh)

        return res
