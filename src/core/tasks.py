from celery import shared_task
from django.utils.timezone import now, timedelta

from events.models import Event

@shared_task
def send_create_booking_notification(user_id, event_id):
    print(f"Уведомление: Пользователь {user_id} забронировал событие {event_id}")

@shared_task
def send_delete_booking_notification(user_id, event_id):
    print(f"Уведомление: Пользователь {user_id} отменил бронь на событие {event_id}")

@shared_task
def send_upcoming_event_notifications():
    target_time_start = now() + timedelta(hours=1)
    target_time_end = target_time_start + timedelta(minutes=1)
    events = Event.objects.prefetch_related('bookings').filter(
        start_time__gte=target_time_start,
        start_time__lt=target_time_end,
        status=Event.PENDING
    )

    for event in events:
        for booking in event.bookings.all():
            print(f"Уведомление: Пользователю {booking.user_id} осталось 1 час до события {event.id}")

@shared_task
def update_event_statuses():
    cutoff_time = now() - timedelta(hours=2)
    events = Event.objects.filter(status=Event.PENDING, start_time__lt=cutoff_time)

    for event in events:
        event.status = Event.COMPLETED
        print(f"Статус события [{event.id}]{event.title}: изменён на 'завершено'")

    Event.objects.bulk_update(events, ["status"])
