from django.contrib.auth.models import User
from django.db import models, transaction
from rest_framework.exceptions import ValidationError


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ("status", "sort_timestamp")

    class Status(models.IntegerChoices):
        PENDING = 1, 'pending'
        COMPLETED = 2, 'completed'
        CANCELLED = 3, 'cancelled'

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    start_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    seats = models.PositiveIntegerField()
    status = models.PositiveIntegerField(choices=Status.choices, default=Status.PENDING)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    sort_timestamp = models.BigIntegerField(db_index=True, default=0)

    def save(self, *args, **kwargs):
        if self.status == self.Status.PENDING:
            self.sort_timestamp = int(self.start_time.timestamp())
        else:
            self.sort_timestamp = -int(self.start_time.timestamp())
        super().save(*args, **kwargs)

    @transaction.atomic
    def create_booking(self, user_id):
        """ Бронирование места на мероприятие """
        if self.bookings.filter(user_id=user_id).exists():
            raise ValidationError('Вы уже забронировали это событие')

        if self.seats <= self.bookings.count():
            raise ValidationError('Мест нет')

        return self.bookings.create(user_id=user_id)

    @transaction.atomic
    def delete_booking(self, user_id):
        """ Отмена бронирования места на мероприятие """
        book = self.bookings.filter(user_id=user_id).first()

        if not book:
            raise ValidationError('Бронирование не найдено')

        book.delete()


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
