import uuid
from django.db import models
from django.conf import settings
from accounts.models import Family


class SyncProvider(models.Model):
    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('microsoft', 'Microsoft Calendar'),
    ]
    SYNC_MODE_CHOICES = [
        ('import', 'Import Only'),
        ('export', 'Export Only'),
        ('bidirectional', 'Bidirectional'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='sync_providers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sync_providers')
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    sync_mode = models.CharField(max_length=13, choices=SYNC_MODE_CHOICES, default='import')
    provider_user = models.CharField(max_length=255, blank=True)
    credentials = models.JSONField(default=dict)
    calendar_mapping = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_provider_type_display()} - {self.family.name}'


class SyncLog(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(SyncProvider, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    events_imported = models.IntegerField(default=0)
    events_exported = models.IntegerField(default=0)
    events_skipped = models.IntegerField(default=0)
    events_failed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.provider} - {self.status} ({self.started_at})'
