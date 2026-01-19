from django.db import models

from apps.cinema import models as CinemaModels
from apps.core import models as CoreModels
from apps.movie import models as MovieModels


class Slot(CoreModels.TimeStampedModel):
    """
    Slot model that contains:
    - **date_time**: date and time of the slot
    - **price**: price of the slot
    - **movie**: foreign key to external Movie relation (many-to-one)
    - **cinema**: foreign key to external Cinema relation (many-to-one)
    - **language**: foreign key to external Language relation (many-to-one)
    - **is_active**: decides whether slot is active or not


    """

    date_time = models.DateTimeField()
    price = models.PositiveIntegerField()
    movie = models.ForeignKey(MovieModels.Movie, on_delete=models.CASCADE)
    cinema = models.ForeignKey(CinemaModels.Cinema, on_delete=models.CASCADE)
    language = models.ForeignKey(CoreModels.Language, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.movie}, {self.cinema}, {self.date_time}"
