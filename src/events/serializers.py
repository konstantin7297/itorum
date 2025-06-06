from rest_framework import serializers

from .models import Event, Booking, Rating, Notification, Tag


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


# class EventSerializer(serializers.ModelSerializer):
#     available_seats = serializers.IntegerField(source='available_seats', read_only=True)
#     average_rating = serializers.SerializerMethodField()
#     tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())
#
#     class Meta:
#         model = Event
#         fields = '__all__'
#
#     def get_average_rating(self, obj):
#         ratings = obj.ratings.all()
#         if ratings.exists():
#             return round(sum(r.score for r in ratings) / ratings.count(), 1)
#         return None
#
#
# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = ['id', 'user', 'event', 'created_at']
#         read_only_fields = ['user', 'created_at']
#
#
# class RatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rating
#         fields = ['id', 'user', 'event', 'score', 'created_at']
#         read_only_fields = ['user', 'created_at']
#
#     def validate(self, data):
#         event = data['event']
#         user = self.context['request'].user
#
#         if event.status != Event.COMPLETED:
#             raise serializers.ValidationError("Оценивать можно только завершённые события")
#
#         if not event.bookings.filter(user=user).exists():
#             raise serializers.ValidationError("Оценивать можно только если вы были участником события")
#
#         return data
#
#
# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'