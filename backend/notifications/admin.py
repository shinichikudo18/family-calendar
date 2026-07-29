from django.contrib import admin
from .models import NotificationChannel, NotificationRule, WebhookEndpoint, WebhookDelivery


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'provider', 'is_enabled', 'verified_at', 'created_at']
    list_filter = ['provider', 'is_enabled']
    search_fields = ['user__username', 'external_recipient_id']


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event_type', 'minutes_before', 'channel', 'is_enabled']
    list_filter = ['event_type', 'is_enabled']


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'target_url', 'is_enabled', 'last_success_at', 'last_error_at']
    list_filter = ['is_enabled']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_type', 'status', 'attempts', 'response_status', 'created_at']
    list_filter = ['status']
