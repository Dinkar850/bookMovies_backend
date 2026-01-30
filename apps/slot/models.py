from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.movie import models as MovieModels


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

    def clean(self):
        """Raises error if one tries to
        - create a slot before its movie's `release_date`
        - create a slot for a movie and cinema before latest slot's end time: `slot's movie duration + slot's buffer_time`
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
            raise ValidationError(
                f"Cannot create a slot before current date and time: {now}"
            )

        # Checks if slot's end_time is being scheduled before or equal to scheduled start_time
        if slot_end <= slot_start:
            raise ValidationError(
                "Cannot enter an time before or equal to the start schedule for this slot"
            )

        # Checks if slot duration is shorter than its movie's duration
        if slot_duration < self.movie.duration:
            raise ValidationError(
                f"Slot duration: {slot_duration} cannot be shorter than movie duration: {self.movie.duration}."
            )

        # Checks if slot is being scheduled before its movie's release_date
        if timezone.localdate(self.schedule) < self.movie.release_date:
            raise ValidationError(
                f"Cannot create a slot for a date before movie's release date: {self.movie.release_date}"
            )

        # Checks if slot is being created for a language other than its movie's
        if not self.movie.language.filter(pk=self.language_id).exists():
            raise ValidationError(
                "Cannot create slot for a language other than its movie's languages."
            )

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
                    f"Cannot create a slot before {prev_end} for this cinema"
                )

        # Checks if slot is being created with an end schedule after an existing slot's start schedule
        if next_slot and slot_end > next_slot.schedule:
            # Combines date and end_time to get the end schedule of the next slot
            next_end = timezone.make_aware(
                datetime.combine(next_slot.schedule.date(), next_slot.end_time),
                timezone.get_current_timezone(),
            )

            raise ValidationError(
                f"Can only create a slot after {next_end} for the given slot's schedule and duration"
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "movie", "cinema"],
                name="unique_slot_per_movie_cinema_schedule",
            )
        ]

    def __str__(self):
        return f"{self.schedule}-{self.movie}-{self.cinema}"
