from django.db import transaction
from rest_framework import serializers

from events.models import Event, Tag


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Event
        fields = [
            "id", "organizer", "title", "description", "start_time", "location",
            "seats", "status", "tags",
        ]
        read_only_fields = ['organizer']

    @transaction.atomic
    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        tags = validated_data.pop('tags', [])
        event = super().create(validated_data)

        add_tags = []
        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag)
            add_tags.append(tag)

        event.tags.set(add_tags)
        return event

    def update(self, instance, validated_data):
        if instance.organizer != self.context['request'].user:
            raise serializers.ValidationError({
                "non_field_errors": "Only the organizer can change the status of an event."
            })

        tags = validated_data.pop('tags', None)
        event = super().update(instance, validated_data)

        if tags:
            event.tags.clear()

            for tag in tags:
                tag, created = Tag.objects.get_or_create(name=tag['name'])
                event.tags.add(tag)

        return event

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['tags'] = [{"id": tag.id, "name": tag.name} for tag in instance.tags.all()]
        return rep
