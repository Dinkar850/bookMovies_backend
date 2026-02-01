from django.db import models
from django.utils.text import slugify

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
    cover_image = models.ImageField(
        upload_to="movie_covers/",
        blank=True,
        null=True,
        help_text="Optional movie's poster shown to users",
    )
    slug = models.SlugField(
        unique=True,
        max_length=250,
        db_index=True,
        editable=False,
    )
    genres = models.ManyToManyField(CoreModels.Genre, related_name="movies")
    languages = models.ManyToManyField(CoreModels.Language, related_name="movies")

    def save(self, *args, **kwargs):
        """Auto-generates a unique slug from movie name with collision handling"""

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            # Keep incrementing and attaching counter till a movie exists for that slug to avoid collision
            while Movie.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
