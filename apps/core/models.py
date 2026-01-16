from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract model to be used for extending following fields:

    - **created_at**: adds a time stamp for entry creation
    - **updated_at**: updates the time stamp on save
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
