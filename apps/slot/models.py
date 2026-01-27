from django.core import exceptions
from django.db import models
from django.utils import timezone

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.movie import models as MovieModels


class Slot(CoreModels.TimeStampedModel):
    """
    Slot model that contains:
    - **schedule**: date and time of the slot
    - **price**: price of the slot
    - **buffer_time**: buffer time for intervals and cleaning per slot
    - **movie**: foreign key to external Movie relation (many-to-one)
    - **cinema**: foreign key to external Cinema relation (many-to-one)
    - **language**: foreign key to external Language relation (many-to-one)
    - **is_active**: decides whether slot is active or not
    """

    is_active = models.BooleanField(
        default=True,
        help_text="Mark false if slot is temporarily cancelled or has expired",
    )
    schedule = models.DateTimeField(help_text="Takes date and time of the slot")
    price = models.PositiveIntegerField()
    buffer_time = models.DurationField(
        blank=True,
        null=True,
        help_text="Enter additional time for intervals / cleaning if applicable",
    )
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

        if not (self.movie_id and self.cinema_id and self.schedule):
            return

        # Checks if slot is being scheduled before its movie's release_date
        if timezone.localdate(self.schedule) < self.movie.release_date:
            raise exceptions.ValidationError(
                f"Cannot create a slot for a date before movie's release date: {self.movie.release_date}"
            )

        # Checks if slot is being created for a language other than its movie's
        if self.language not in self.movie.language:
            raise exceptions.ValidationError(
                f"Cannot create slot for a language other than its movie's languages: {self.movie.language}"
            )

        latest_slot = (
            Slot.objects.filter(
                movie_id=self.movie_id,
                cinema_id=self.cinema_id,
                schedule__lt=self.schedule,
                is_active=True,
            )
            .exclude(pk=self.pk)
            .select_related("movie")
            .order_by("-schedule")
            .first()
        )

        if not latest_slot:
            return

        latest_slot_end = (
            latest_slot.schedule + latest_slot.movie.duration + latest_slot.buffer_time
        )

        # Checks if slot is being created before the last slot has been finished (slot's movie duration + buffer_time)
        if self.schedule < latest_slot_end:
            raise exceptions.ValidationError(
                f"Cannot create a slot before {latest_slot_end} for this movie and cinema"
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "movie", "cinema"],
                name="unique_slot_per_movie_cinema_schedule",
            )
        ]

    def __str__(self):
        return f"{self.schedule}, {self.movie}, {self.cinema}, {self.language}"
