from django.db import models

from apps.core import models as CoreModels


class Genre(CoreModels.TimeStampedModel):
    """
    Genre model that contains:

    - **name**: name of the genre
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Movie(CoreModels.TimeStampedModel):
    """
    Movie model that contains:

    - **name**: name of the movie
    - **description**: description of the movie
    - **duration**: duration of the movie
    - **release_date**: release date of the movie
    - **cover_image**: cover image of the movie
    - **genre**: foreign key to external City relation (many-to-many)
    - **language**: foreign key to external Language relation (many-to-many)
    """

    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    duration = models.DurationField()
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to="movie_covers/", blank=True, null=True)
    genre = models.ManyToManyField(Genre)
    language = models.ManyToManyField(CoreModels.Language)

    def __str__(self):
        return self.name
