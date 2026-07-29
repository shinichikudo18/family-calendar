from rest_framework import serializers
from .models import Calendar, Event, EventParticipant, EventCategory


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventParticipantSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = EventParticipant
        fields = ['id', 'event', 'user', 'user_details', 'status']
        read_only_fields = ['id']

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
        }


class EventSerializer(serializers.ModelSerializer):
    participants = EventParticipantSerializer(many=True, read_only=True)
    calendar_name = serializers.CharField(source='calendar.name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class EventCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by',
                            'external_id', 'external_provider']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        validated_data['created_by'] = self.context['request'].user
        event = super().create(validated_data)
        for user_id in participants_data:
            EventParticipant.objects.create(event=event, user_id=user_id)
        return event


class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'
        read_only_fields = ['id']
