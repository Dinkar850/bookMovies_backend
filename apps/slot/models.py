from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.movie import models as MovieModels

from .constants import SlotErrors


class Slot(CoreModels.TimeStampedModel, CoreModels.ActiveableModel):
    """
    Slot model that contains:
    - **schedule**: start date and time of the slot
    - **end_time**: end time of the slot
    - **price**: price of the slot
    - **movie**: foreign key to external Movie relation (many-to-one)
    - **cinema**: foreign key to external Cinema relation (many-to-one)
    - **language**: foreign key to external Language relation (many-to-one)
    """

    schedule = models.DateTimeField(help_text="Takes start date and time of the slot")
    end_time = models.TimeField(help_text="Takes end time of the slot")
    price = models.PositiveIntegerField()
    movie = models.ForeignKey(
        MovieModels.Movie, on_delete=models.CASCADE, related_name="slots"
    )
    cinema = models.ForeignKey(
        CinemaModels.Cinema, on_delete=models.CASCADE, related_name="slots"
    )
    language = models.ForeignKey(
        CoreModels.Language, on_delete=models.CASCADE, related_name="slots"
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
        slot_end = timezone.make_aware(
            datetime.combine(self.schedule.date(), self.end_time),
            timezone.get_current_timezone(),
        )
        slot_duration = slot_end - slot_start

        # Checks if slot is being created before current time and date
        if slot_start < now:
            raise ValidationError(f"{SlotErrors.BEFORE_NOW}: {now}")

        # Checks if slot duration is shorter than its movie's duration
        if slot_duration < self.movie.duration:
            raise ValidationError(
                f"{SlotErrors.INSUFFICIENT_DURATION}: {self.movie.duration}."
            )

        # Checks if slot is being scheduled for a date before its movie's release_date
        if timezone.localdate(self.schedule) < self.movie.release_date:
            raise ValidationError(
                f"{SlotErrors.BEFORE_MOVIE_RELEASE}: {self.movie.release_date}"
            )

        # Checks if slot is being created for a language other than its movie's languages
        if not self.movie.languages.filter(pk=self.language_id).exists():
            raise ValidationError(SlotErrors.INVALID_LANGUAGE)

        previous_slot = (
            Slot.objects.filter(
                cinema_id=self.cinema_id,
                schedule__lt=self.schedule,
                is_active=True,
            )
            .exclude(pk=self.pk)
            .order_by("-schedule")
            .first()
        )

        next_slot = (
            Slot.objects.filter(
                cinema_id=self.cinema_id,
                schedule__gt=self.schedule,
                is_active=True,
            )
            .exclude(pk=self.pk)
            .order_by("schedule")
            .first()
        )

        # Checks if slot is being created before the previous slot has been finished
        if previous_slot:
            # Combines date and end_time to get the end schedule of the previous slot
            prev_end = timezone.make_aware(
                datetime.combine(previous_slot.schedule.date(), previous_slot.end_time),
                timezone.get_current_timezone(),
            )

            if slot_start < prev_end:
                raise ValidationError(
                    f"{SlotErrors.OVERLAPS_PREVIOUS_SLOT}: {prev_end}"
                )

        # Checks if slot is being created with an end schedule after an existing slot's start schedule
        if next_slot and slot_end > next_slot.schedule:
            # Combines date and end_time to get the end schedule of the next slot
            next_end = timezone.make_aware(
                datetime.combine(next_slot.schedule.date(), next_slot.end_time),
                timezone.get_current_timezone(),
            )

            raise ValidationError(f"{SlotErrors.OVERLAPS_NEXT_SLOT}: {next_end}")

    def __str__(self):
        return self.schedule.strftime("%d %b %H:%M")
