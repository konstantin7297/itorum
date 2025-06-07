from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
