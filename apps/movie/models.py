from django.db import models
from django.utils import text

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

    name = models.CharField(
        max_length=250, unique=True, help_text="Maximum 250 characters are allowed"
    )
    description = models.TextField(blank=True)
    duration = models.DurationField()
    release_date = models.DateField()
    cover_image = models.ImageField(
        upload_to="movie_covers/",
        blank=True,
        null=True,
        help_text="Upload the movie's poster if exists",
    )
    slug = models.SlugField(
        unique=True,
        max_length=250,
        db_index=True,
        editable=False,
    )
    genre = models.ManyToManyField(CoreModels.Genre, related_name="movies")
    language = models.ManyToManyField(CoreModels.Language, related_name="movies")

    def save(self, *args, **kwargs):
        """Adds slug for movie based on movie's name. Gets called on each instance creation / updation"""
        if not self.slug:
            self.slug = text.slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns canonical url for each movie's resource"""
        return f"/movies/{self.slug}"

    def __str__(self):
        return self.name
