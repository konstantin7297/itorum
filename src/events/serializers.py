from rest_framework import serializers

from events.models import Event, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        event = super().create(validated_data)

        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag['name'])
            event.tags.add(tag)

        return event

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        event = super().update(instance, validated_data)

        if tags:
            event.tags.clear()

            for tag in tags:
                tag, created = Tag.objects.get_or_create(name=tag['name'])
                event.tags.add(tag)

        return event
