from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True
    )
    telegram_username = models.CharField(
        max_length=100
    )
    notifications = models.BooleanField(
        default=False
    )
    city = models.CharField(
        max_length=50,
        default="Москва"
    )
    zodiac = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.telegram_username
