from django.contrib.postgres.indexes import GinIndex
from django.contrib.auth.models import User
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    PENDING = 'pending'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (PENDING, 'Ожидается'),
        (CANCELLED, 'Отменено'),
        (COMPLETED, 'Завершено'),
    ]

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        indexes = [
            GinIndex(fields=['description'], name='gin_event_description'),
        ]

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    start_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    class Meta:
        unique_together = ('user', 'event')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
