from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Menu(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))],
    )
    inventory = models.PositiveIntegerField()

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="menu_nonnegative_price"),
        ]

    def __str__(self):
        return self.title


class Booking(models.Model):
    name = models.CharField(max_length=255)
    no_of_guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    booking_date = models.DateTimeField()

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(no_of_guests__gte=1), name="booking_has_guests"),
        ]

    def __str__(self):
        return self.name
