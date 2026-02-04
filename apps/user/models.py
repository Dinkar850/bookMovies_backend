from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import ActiveableModel, TimeStampedModel
from apps.user.managers import UserManager

# Validates that phone number has exactly 10 digits and does not start with 0
phone_validator = RegexValidator(
    regex=r"^[1-9]\d{9}$",
    message="Phone number must be exactly 10 digits and cannot start with 0",
)


class User(
    TimeStampedModel,
    ActiveableModel,
    AbstractBaseUser,
    PermissionsMixin,
):
    """
    Initialises a custom user model for email based login

    Contains:
    - **is_staff**: enables user login in admin panel
    - **email**: user's email address and acts as the unique identifier
    - **first_name**: user's first name
    - **last_name**: user's last name ( optional)
    - **phone_number**: user's 10 digit phone number, unique
    - **profile_image**: user's profile image(optional)
    - **required_fields**: `first_name`, `phone_number`, `email` and `password`
    - Permisions from PermissionsMixin contains `is_superuser`, `has_perm`, `group` permissions
    - Custom user manager: `UserManager`
    """

    is_staff = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70, blank=True)
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator],
        help_text="Maximum 10 digits are allowed and should not start with 0",
    )
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "phone_number")

    objects = UserManager()

    def __str__(self):
        return self.email
