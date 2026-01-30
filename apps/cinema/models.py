from django.core import exceptions, validators
from django.db import models, transaction

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

    name = models.CharField(
        max_length=250, help_text="Maximum 250 characters are allowed"
    )
    rows = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(5)],
        help_text="Specify total rows of seats in the cinema, minimum 5 are required",
    )
    seats_per_row = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(5)],
        help_text="Minimum 5 seats per row are required",
    )
    address = models.TextField()
    city = models.ForeignKey(
        CoreModels.City, on_delete=models.CASCADE, related_name="cinemas"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "address", "city"],
                name="unique_cinema_per_address_city",
            )
        ]

    def __str__(self):
        return f"{self.name}, {self.address}, {self.city}"

    def save(self, *args, **kwargs):
        """Creates or updates cinema, if cinema is created, also creates the new seats for that cinema"""

        is_unique = self.pk is None

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_unique:
                self._create_seats()
            else:
                self._update_seats()

    def _create_seats(self):
        """Creates seats for new cinema being created"""

        seats = [
            Seat(seat_row=row + 1, seat_number=number + 1, cinema=self)
            for row in range(self.rows)
            for number in range(self.seats_per_row)
        ]

        Seat.objects.bulk_create(seats)

    def _update_seats(self):
        """
        Updates seats with the following criterias:
        - Activate seats if they already exist and required in updated `rows`, `seats_per_row`
        - Deactivate seats if `rows` or `seats_per_row` is decreased
        - Create new seats if `rows` or `seats_per_row` is increased
        """

        existing_seats = {
            (seat.seat_row, seat.seat_number): seat
            for seat in Seat.objects.filter(cinema=self)
        }

        required_seats = {
            (row + 1, number + 1)
            for row in range(self.rows)
            for number in range(self.seats_per_row)
        }

        to_create = []
        to_activate = []
        to_deactivate = []

        for position in required_seats:
            # Creates new seat if required and is not present in existing seats
            if position not in existing_seats:
                to_create.append(
                    Seat(seat_row=position[0], seat_number=position[1], cinema=self)
                )

            # Activates seat if required and is present in existing seat
            elif not existing_seats[position].is_active:
                existing_seats[position].is_active = True
                to_activate.append(existing_seats[position])

        for position, seat in existing_seats.items():
            # Deactivates existing and active seats not present in required seats
            if position not in required_seats and seat.is_active:
                seat.is_active = False
                to_deactivate.append(seat)

        # Bulk create status of required seats
        if to_create:
            Seat.objects.bulk_create(to_create)

        # Bulk update status of required seats
        if to_activate or to_deactivate:
            Seat.objects.bulk_update(to_activate + to_deactivate, ["is_active"])


class Seat(CoreModels.TimeStampedModel, CoreModels.ActiveableModel):
    """
    Seat model that contains:
    - **seat_row**: row corresponding to the seat
    - **seat_number**: position of seat in that row
    - **cinema**: foreign key reference to cinema (many-to-one)
    """

    seat_row = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        help_text="Specify row of the seat (1-indexed)",
    )
    seat_number = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(1)],
        help_text="Specify position of the seat in the row (1-indexed)",
    )
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="seats")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["seat_row", "seat_number", "cinema"],
                name="unique_seat_per_cinema",
            )
        ]

    def clean(self):
        """
        Raises exception in admin panel only, if:
        - entered seat row is not in defined range
        - entered seat number is not in defined range
        """

        super().clean()

        # Checks if entered seat row is greater than rows for the linked cinema
        if self.seat_row > self.cinema.rows:
            raise exceptions.ValidationError(
                f"Row must be between 1 and {self.cinema.rows}"
            )

        # Checks if entered seat number is greater than seats for the linked cinema
        if self.seat_number > self.cinema.seats_per_row:
            raise exceptions.ValidationError(
                f"Seat number must be between 1 and {self.cinema.seats_per_row}"
            )

    def __str__(self):
        return f"{self.seat_row},{self.seat_number}-{self.cinema}"
