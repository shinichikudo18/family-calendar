from rest_framework import serializers
from .models import NotificationChannel, NotificationRule, WebhookEndpoint, WebhookDelivery


class NotificationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationChannel
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = '__all__'
        read_only_fields = ['id']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'name', 'target_url', 'allowed_event_types',
                  'is_enabled', 'last_success_at', 'last_error_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'last_success_at', 'last_error_at',
                            'created_at', 'updated_at']


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AutomationEventSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    all_day = serializers.BooleanField(default=False)
    calendar_id = serializers.UUIDField(required=False)
