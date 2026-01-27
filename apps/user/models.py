from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from apps.core import models as CoreModels

from .managers import UserManager

# Validates that phone number has exactly 10 digits and none are characters other than digits
phone_validator = RegexValidator(
    regex=r"^[1-9]\d{9}$",
    message="Phone number must be exactly 10 digits and cannot start with 0.",
)


class User(CoreModels.TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    """
    Initialises a custom user model for email based login

    Contains:
    - **email**: user's email address and acts as the unique identifier
    - **first_name**: user's first name
    - **last_name**: user's last name (is optional)
    - **phone_number**: user's 10 digit phone number, unique
    - **profile_image**: user's profile image(optional)
    - **is_active**: mimics default user's is active state of user
    - **is_staff**: enables user login in admin panel
    - **required_fields**: first_name, phone_number, email and password
    - Permisions from PermissionsMixin contains is_superuser, has_perm, group permissions
    - Custom user manager: UserManager
    """

    email = models.EmailField(
        max_length=255, unique=True, help_text="Maximum 255 characters are allowed"
    )
    first_name = models.CharField(
        max_length=70, help_text="Maximum 70 characters are allowed"
    )
    last_name = models.CharField(
        max_length=70,
        blank=True,
        help_text="Maximum 70 characters are allowed, can be left blank",
    )
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator],
        help_text="Maximum 10 digits are allowed and should not start with 0",
    )
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.email
