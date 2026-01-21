from django.db import models

from apps.core import models as CoreModels


class Movie(CoreModels.TimeStampedModel):
    """
    Movie model that contains:

    - **name**: name of the movie
    - **description**: description of the movie
    - **duration**: duration of the movie
    - **release_date**: release date of the movie
    - **cover_image**: cover image of the movie
    - **genre**: foreign key reference to genre (many-to-many)
    - **language**: foreign key reference to language (many-to-many)
    """

    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    duration = models.DurationField()
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to="movie_covers/", blank=True, null=True)
    genre = models.ManyToManyField(CoreModels.Genre, related_name="movies")
    language = models.ManyToManyField(CoreModels.Language, related_name="movies")

    def __str__(self):
        return self.name
