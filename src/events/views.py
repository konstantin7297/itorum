from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F, Count
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, \
    ChoiceFilter, DateFilter, BooleanFilter, ModelMultipleChoiceFilter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from utils.tasks import send_create_booking_notification, send_delete_booking_notification
from events.models import Event, Tag
from events.serializers import EventSerializer


class EventFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск по описанию')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all(),
        conjoined=False,
    )
    location = CharFilter(field_name='location', lookup_expr='icontains')
    status = ChoiceFilter(field_name='status', choices=Event.Status.choices)
    date = DateFilter(field_name='start_time', lookup_expr='date')
    free_seats = BooleanFilter(method='filter_free_seats')

    class Meta:
        model = Event
        fields = ['search', 'tags', 'location', 'status', 'date', 'free_seats']

    def filter_free_seats(self, queryset, name, value):
        if value:
            return queryset \
                .annotate(booked_count=Count('bookings')) \
                .filter(seats__gt=F('booked_count'))
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset \
            .annotate(rank=SearchRank(SearchVector('description'), SearchQuery(value))) \
            .filter(rank__gte=0.1).order_by('-rank')


class EventView(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Event.objects.prefetch_related('bookings', 'tags').all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter

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
        event.create_booking(request.user.id)
        send_create_booking_notification.delay(request.user.id, event.id)
        return Response({'status': 'Бронирование успешно'}, status=201)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_booking(self, request, pk=None):
        """ Отменяет бронь места на событие """
        event = self.get_object()
        event.delete_booking(request.user.id)
        send_delete_booking_notification.delay(request.user.id, event.id)
        return Response({'status': 'Бронирование отменено'}, status=200)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        """ Показывает ближайшие события пользователя """
        user = request.user
        events = self.queryset.filter(
            bookings__user=user,
            start_time__gte=now(),
            status=Event.Status.PENDING
        ).distinct()

        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
