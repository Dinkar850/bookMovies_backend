from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email, password and additional fields.
        """
        if not email:
            raise ValueError("Users must have an email")

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email, password and additional fields.
        """
        user = self.create_user(
            email, password, is_staff=True, is_superuser=True, **extra_fields
        )

        user.save()
        return user
