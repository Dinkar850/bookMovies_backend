from django.db import models
from django.utils import timezone

from apps.core.managers import ActiveManager


class TimeStampedModel(models.Model):
    """
    Abstract model to be used for extending following fields:

    - **created_at**: adds a time stamp for entry creation
    - **updated_at**: updates the time stamp on save
    """

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveableModel(models.Model):
    """
    Abstract model forL
    - adding an active state using `is_active` boolean field
    - a custom `active_objects` manager for filtering out only `active` entries
    """

    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True


class Language(TimeStampedModel):
    """
    Language model that contains:

    - **name**: name of the language
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class City(TimeStampedModel):
    """
    City model that contains:

    - **name**: name of the city
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(TimeStampedModel):
    """
    Genre model that contains:

    - **name**: name of the genre
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
