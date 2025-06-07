from django.db.models import Q, QuerySet, F, Count
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, \
    ChoiceFilter, DateFilter, BooleanFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.tasks import send_create_booking_notification, send_delete_booking_notification
from .models import Event
from .serializers import EventSerializer


class EventFilter(FilterSet):
    location = CharFilter(field_name='location', lookup_expr='icontains')
    status = ChoiceFilter(field_name='status', choices=Event.STATUS_CHOICES)
    date = DateFilter(field_name='start_time', lookup_expr='date')
    free_seats = BooleanFilter(method='filter_free_seats')

    class Meta:
        model = Event
        fields = ['location', 'status', 'date', 'free_seats']

    def filter_free_seats(self, queryset, name, value):
        if value:
            return queryset \
                .annotate(booked_count=Count('bookings')) \
                .filter(seats__gt=F('booked_count'))
        return queryset


class EventView(ModelViewSet):  # TODO: Пагинацию поправить? т.к. sorting_events отдает список а не кс.
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Event.objects.prefetch_related('bookings').all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter

    def sorting_events(self, events: QuerySet) -> list:
        """ Своя сортировка событий для отдачи """
        current_time = now()

        upcoming = events \
            .filter(start_time__gte=current_time, status=Event.PENDING) \
            .order_by('start_time')

        past_cancelled = events \
            .filter(Q(start_time__lt=current_time) | Q(status__in=[Event.CANCELLED, Event.COMPLETED])) \
            .exclude(Q(start_time__gte=current_time, status=Event.PENDING)) \
            .order_by('-start_time')

        return list(upcoming) + list(past_cancelled)

    def perform_create(self, serializer):
        """ Создание события """
        serializer.save(organizer=self.request.user)

    def list(self, request, *args, **kwargs):
        """ Получение списка всех событий """
        events = self.filter_queryset(self.get_queryset())
        sorted_events = self.sorting_events(events)
        serializer = self.get_serializer(sorted_events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """ Обновляет событие """
        event = self.get_object()

        if event.organizer != request.user:
            return Response(
                {"detail": "Изменять статус события может только организатор."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """ Удаляет событие """
        event = self.get_object()
        if event.organizer != request.user:
            return Response(
                {"detail": "Удалять событие может только организатор."},
                status=status.HTTP_403_FORBIDDEN
            )

        time_diff = now() - event.created_at
        if time_diff.total_seconds() > 3600:
            return Response(
                {"detail": "Удаление возможно только в течение 1 часа после создания."},
                status=status.HTTP_403_FORBIDDEN
                )

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_booking(self, request, pk=None):
        """ Бронирует место на событие """
        event = self.get_object()
        user = request.user

        if event.bookings.filter(user=user).exists():
            return Response(
                {'detail': 'Вы уже забронировали это событие'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.seats <= event.bookings.count():
            return Response(
                {'detail': 'Мест нет'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.bookings.create(user=user)
        send_create_booking_notification.delay(user.id, event.id)

        return Response(
            {'status': 'Бронирование успешно'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_booking(self, request, pk=None):
        """ Отменяет бронь места на событие """
        event = self.get_object()
        user = request.user

        booking = event.bookings.filter(user=user).first()
        if not booking:
            return Response(
                {'detail': 'Бронирование не найдено'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.delete()
        send_delete_booking_notification.delay(user.id, event.id)

        return Response(
            {'status': 'Бронирование отменено'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        """ Показывает ближайшие события пользователя """
        user = request.user
        events = self.queryset.filter(
            bookings__user=user,
            start_time__gte=now(),
            status=Event.PENDING
        ).distinct().order_by('start_time')

        sorted_events = self.sorting_events(events)
        serializer = self.get_serializer(sorted_events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
