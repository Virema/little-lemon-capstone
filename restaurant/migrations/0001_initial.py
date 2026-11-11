from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("no_of_guests", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("booking_date", models.DateTimeField()),
            ],
            options={
                "ordering": ["id"],
                "constraints": [models.CheckConstraint(condition=models.Q(no_of_guests__gte=1), name="booking_has_guests")],
            },
        ),
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal("0.00"))])),
                ("inventory", models.PositiveIntegerField()),
            ],
            options={
                "ordering": ["id"],
                "constraints": [models.CheckConstraint(condition=models.Q(price__gte=0), name="menu_nonnegative_price")],
            },
        ),
    ]
