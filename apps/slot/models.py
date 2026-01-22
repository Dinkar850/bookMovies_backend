from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.movie import models as MovieModels


class Slot(CoreModels.TimeStampedModel):
    """
    Slot model that contains:
    - **date_time**: date and time of the slot
    - **price**: price of the slot
    - **buffer_time**: buffer time for intervals and cleaning per slot
    - **movie**: foreign key to external Movie relation (many-to-one)
    - **cinema**: foreign key to external Cinema relation (many-to-one)
    - **language**: foreign key to external Language relation (many-to-one)
    - **is_active**: decides whether slot is active or not
    """

    is_active = models.BooleanField(default=True)
    date_time = models.DateTimeField()
    price = models.PositiveIntegerField()
    buffer_time = models.DurationField(blank=True, null=True)
    movie = models.ForeignKey(
        MovieModels.Movie, on_delete=models.CASCADE, related_name="slots"
    )
    cinema = models.ForeignKey(
        CinemaModels.Cinema, on_delete=models.CASCADE, related_name="slots"
    )
    language = models.ForeignKey(
        CoreModels.Language, on_delete=models.CASCADE, related_name="slots"
    )

    def clean(self):
        """Raises error if one tries to
        - create a slot before its movie's `release_date`
        - create a slot for a movie and cinema before latest slot's end time: `slot's movie duration + slot's buffer_time`
        """
        super().clean()

        if not (self.movie_id and self.cinema_id and self.date_time):
            return

        if timezone.localdate(self.date_time) < self.movie.release_date:
            raise ValidationError(
                f"Cannot create a slot for a date before movie's release date: {self.movie.release_date}"
            )

        latest_slot = (
            Slot.objects.filter(
                movie_id=self.movie_id,
                cinema_id=self.cinema_id,
                date_time__lt=self.date_time,
                is_active=True,
            )
            .exclude(pk=self.pk)
            .select_related("movie")
            .order_by("-date_time")
            .first()
        )

        if not latest_slot:
            return

        latest_slot_end = (
            latest_slot.date_time + latest_slot.movie.duration + latest_slot.buffer_time
        )

        if self.date_time < latest_slot_end:
            raise ValidationError(
                f"Cannot create a slot before {latest_slot_end} for this movie and cinema"
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date_time", "movie", "cinema"],
                name="unique_slot_per_movie_cinema_date_time",
            )
        ]

    def __str__(self):
        return f"{self.date_time}, {self.movie}, {self.cinema}, {self.language}"
