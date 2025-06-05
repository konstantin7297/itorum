from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидается'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    title = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", max_length=500)
    start_time = models.DateTimeField("Время начала")
    location = models.CharField("Локация", max_length=100)
    seats = models.PositiveIntegerField("Количество мест")
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='pending')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Организатор", related_name='events')

    def __str__(self):
        return self.title


class Notification(models.Model):
    pass
