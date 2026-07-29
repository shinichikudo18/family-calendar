import uuid
import hashlib
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet


def generate_encryption_key():
    return Fernet.generate_key()


def encrypt_value(value: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(value.encode())


def decrypt_value(encrypted: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted).decode()


class NotificationChannel(models.Model):
    PROVIDER_CHOICES = [
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_channels'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    external_recipient_id = models.CharField(max_length=255)
    is_enabled = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'provider', 'external_recipient_id')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_provider_display()} - {self.external_recipient_id}'


class NotificationRule(models.Model):
    EVENT_TYPE_CHOICES = [
        ('event_reminder', 'Recordatorio de evento'),
        ('daily_summary', 'Resumen diario'),
        ('weekly_summary', 'Resumen semanal'),
        ('sync_error', 'Error de sincronización'),
        ('token_expiring', 'Token próximo a vencer'),
        ('calendar_conflict', 'Conflicto de calendario'),
        ('backup_error', 'Error de respaldo'),
        ('event_created', 'Evento creado desde bot'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notification_rules'
    )
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    minutes_before = models.IntegerField(default=0)
    channel = models.ForeignKey(
        NotificationChannel, on_delete=models.CASCADE,
        related_name='rules'
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['event_type', 'minutes_before']

    def __str__(self):
        return f'{self.get_event_type_display()} -> {self.channel}'


class WebhookEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    target_url = models.URLField(max_length=1024)
    encrypted_signing_secret = models.BinaryField()
    allowed_event_types = models.JSONField(default=list)
    is_enabled = models.BooleanField(default=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def set_signing_secret(self, secret: str):
        key = settings.SECRET_KEY.encode()[:32]
        key = key.ljust(32, b'\0')[:32]
        fernet_key = Fernet.generate_key()
        self.encrypted_signing_secret = fernet_key + b'::' + encrypt_value(secret, fernet_key)

    def get_signing_secret(self) -> str:
        parts = self.encrypted_signing_secret.split(b'::', 1)
        if len(parts) != 2:
            return ''
        fernet_key, encrypted = parts
        return decrypt_value(encrypted, fernet_key)


class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('success', 'Entregado'),
        ('failed', 'Fallido'),
        ('retrying', 'Reintentando'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        WebhookEndpoint, on_delete=models.CASCADE,
        related_name='deliveries'
    )
    event_type = models.CharField(max_length=50)
    payload_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    attempts = models.IntegerField(default=0)
    response_status = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.event_type} - {self.status}'
