import uuid
from django.db import models
from django.conf import settings
from accounts.models import Family


class Calendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name='calendars'
    )
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#3B82F6')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_calendars'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('family', 'name')

    def __str__(self):
        return f'{self.family.name} - {self.name}'


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    calendar = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name='events'
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=500, blank=True)
    color = models.CharField(max_length=7, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_events'
    )
    external_id = models.CharField(max_length=500, blank=True)
    external_provider = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['calendar', 'start_time']),
            models.Index(fields=['external_id', 'external_provider']),
        ]

    def __str__(self):
        return self.title


class EventParticipant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptado'),
        ('maybe', 'Tal vez'),
        ('declined', 'Rechazado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='event_participations'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.event.title} ({self.get_status_display()})'


class EventCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name='event_categories'
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6B7280')

    class Meta:
        verbose_name_plural = 'event categories'
        unique_together = ('family', 'name')

    def __str__(self):
        return self.name
