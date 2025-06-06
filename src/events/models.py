from django.contrib.auth.models import User
from django.db import models


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

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    start_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')


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
    sent = models.BooleanField(default=False)


class Rating(models.Model):
    SCORE_CHOICES = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    class Meta:
        unique_together = ('user', 'event')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):  # TODO: теги для событий (многие-ко-многим).
    pass
