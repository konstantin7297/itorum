from celery import shared_task
from django.utils.timezone import now, timedelta

from events.models import Event, Notification

@shared_task
def send_create_booking_notification(user_id, event_id):
    """ Какая-то логика для отправки уведомлений по бронированию """
    message = f"Уведомление: Пользователь {user_id} забронировал событие {event_id}"
    Notification.objects.create(user=user_id, event=event_id, message=message)

@shared_task
def send_delete_booking_notification(user_id, event_id):
    """ Какая-то логика для отправки уведомлений по отмене бронирования """
    message = f"Уведомление: Пользователь {user_id} отменил бронь на событие {event_id}"
    Notification.objects.create(user=user_id, event=event_id, message=message)

@shared_task
def send_upcoming_event_notifications():
    """ Какая-то логика для отправки уведомлений по скорому началу события """
    target_time_start = now() + timedelta(hours=1)
    target_time_end = target_time_start + timedelta(minutes=1)
    events = Event.objects.prefetch_related('bookings').filter(
        start_time__gte=target_time_start,
        start_time__lt=target_time_end,
        status=Event.PENDING
    )

    notifications = []
    for event in events:
        for booking in event.bookings.all():
            message = f"Уведомление: Пользователю {booking.user_id} осталось 1 час до события {event.id}"
            notifications.append(Notification(user=booking.user_id, event=event.id, message=message))

    Notification.objects.bulk_create(notifications)

@shared_task
def update_event_statuses():
    """ Периодическое переключение статуса пройденных событий """
    cutoff_time = now() - timedelta(hours=2)
    events = Event.objects.filter(status=Event.PENDING, start_time__lt=cutoff_time)

    for event in events:
        event.status = Event.COMPLETED
        # print(f"Статус события [{event.id}]{event.title}: изменён на 'завершено'")

    Event.objects.bulk_update(events, ["status"])
