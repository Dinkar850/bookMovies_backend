from django.db import models

from apps.core import models as CoreModels


class Cinema(CoreModels.TimeStampedModel):
    """
    Cinema model that contains:

    - **name**: non unique name of the cinema
    - **rows**: number of rows in cinema
    - **seats_per_rows**: number of seats per row in cinema
    - **address**: block, street name of the cinema's location
    - **city**: foreign key to external City relation (many-to-one)
    """

    name = models.CharField(max_length=250)
    rows = models.PositiveIntegerField()
    seats_per_row = models.IntegerField()
    address = models.TextField()
    city = models.ForeignKey(CoreModels.City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.address}, {self.city}"
