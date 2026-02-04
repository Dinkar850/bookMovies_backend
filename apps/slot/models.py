from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.cinema.models import Cinema
from apps.core.models import ActiveableModel, Language, TimeStampedModel
from apps.movie.models import Movie
from apps.slot.constants import SlotErrors


class Slot(TimeStampedModel, ActiveableModel):
    """
    Slot model that contains:
    - **schedule**: start date and time of the slot
    - **end_schedule**: end date and time of the slot
    - **price**: price of the slot
    - **movie**: foreign key to external Movie relation (many-to-one)
    - **cinema**: foreign key to external Cinema relation (many-to-one)
    - **language**: foreign key to external Language relation (many-to-one)
    """

    schedule = models.DateTimeField(help_text="Takes start date and time of the slot")
    end_schedule = models.DateTimeField(help_text="Takes end date and time of the slot")
    price = models.PositiveIntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="slots")
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="slots")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="slots"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("schedule", "movie", "cinema"),
                name="unique_slot_per_movie_cinema_schedule",
            )
        ]

    def clean(self):
        """Custom clean method for validating slot creation in admin panel where slot cannot be created for a:
        - schedule before current date and time
        - duration lesser than its movie's duration
        - schedule before its movie's release date
        - language other than its movie's languages
        - schedule and duration overlapping with an existing slot
        """

        super().clean()
        now = timezone.now()

        if not (self.movie_id and self.cinema_id and self.schedule):
            return

        slot_start = self.schedule
        slot_end = self.end_schedule

        slot_duration = slot_end - slot_start

        # Validation: Slot' is being scheduled before current time and date'
        if slot_start < now:
            raise ValidationError(f"{SlotErrors.BEFORE_NOW}: {now}")

        # Validation: Slot's duration is either 0 or negative
        if slot_end <= slot_start:
            raise ValidationError(SlotErrors.INVALID_DURATION)

        # Validation: Slot's duration is shorter than its movie's duration
        if slot_duration < self.movie.duration:
            raise ValidationError(
                f"{SlotErrors.INSUFFICIENT_DURATION}: {self.movie.duration}."
            )

        # Validation: Slot is being scheduled for a date before its movie's release_date
        if timezone.localdate(self.schedule) < self.movie.release_date:
            raise ValidationError(
                f"{SlotErrors.BEFORE_MOVIE_RELEASE}: {self.movie.release_date}"
            )

        # Validation: Slot is being scheduled for a language other than its movie's languages
        if not self.movie.languages.filter(pk=self.language_id).exists():
            raise ValidationError(SlotErrors.INVALID_LANGUAGE)

        # Validation: Slot is overlapping with an existing slot for the same cinema
        overlapping_slot = Slot.objects.exclude(pk=self.pk).filter(
            cinema=self.cinema,
            schedule__lt=self.end_schedule,
            end_schedule__gt=self.schedule,
        )

        if overlapping_slot.exists():
            raise ValidationError(SlotErrors.OVERLAPPING_SLOT)

    def __str__(self):
        return self.schedule.strftime("%d %b %H:%M")
