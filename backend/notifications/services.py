import logging
import json
import requests
from django.conf import settings
from django.utils import timezone
from .models import NotificationChannel, NotificationRule, WebhookEndpoint
from .webhook_utils import deliver_webhook

logger = logging.getLogger(__name__)


N8N_WEBHOOK_BASE = getattr(settings, 'N8N_URL', 'https://brain.katherine.cl:88')


def send_notification(channel: NotificationChannel, title: str, message: str, event_type: str = 'notification'):
    payload = {
        'to': channel.external_recipient_id,
        'provider': channel.provider,
        'title': title,
        'message': message,
        'event_type': event_type,
        'timestamp': timezone.now().isoformat(),
    }
    try:
        resp = requests.post(
            f'{N8N_WEBHOOK_BASE}/webhook/family-calendar-notify',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-FamilyCalendar-Source': 'django',
            },
            timeout=15,
        )
        if resp.status_code < 300:
            logger.info(f'Notification sent to {channel.provider}: {channel.external_recipient_id}')
            return True
        logger.warning(f'n8n returned {resp.status_code}: {resp.text[:200]}')
        return False
    except requests.RequestException as e:
        logger.error(f'n8n notification failed: {e}')
        return False


def send_event_reminder(event, minutes_before: int):
    from events.models import EventParticipant
    participants = EventParticipant.objects.filter(event=event, status='accepted')
    for participant in participants:
        channels = NotificationChannel.objects.filter(
            user=participant.user, is_enabled=True
        )
        for channel in channels:
            send_notification(
                channel,
                f'Recordatorio: {event.title}',
                f'En {minutes_before} minutos: {event.title}\n{event.start_time.strftime("%H:%M")} - {event.end_time.strftime("%H:%M")}',
                'event_reminder',
            )


def send_daily_summary(user, events):
    channels = NotificationChannel.objects.filter(user=user, is_enabled=True)
    if not events:
        return
    lines = ['Resumen diario:']
    for e in events:
        lines.append(f'- {e.start_time.strftime("%H:%M")} {e.title}')
    message = '\n'.join(lines)
    for channel in channels:
        send_notification(channel, 'Resumen diario', message, 'daily_summary')


def send_weekly_summary(user, events):
    channels = NotificationChannel.objects.filter(user=user, is_enabled=True)
    if not events:
        return
    lines = ['Resumen semanal:']
    for e in events:
        lines.append(f'- {e.start_time.strftime("%a %d")} {e.title}')
    message = '\n'.join(lines)
    for channel in channels:
        send_notification(channel, 'Resumen semanal', message, 'weekly_summary')


def notify_sync_error(provider, error_msg):
    from accounts.models import FamilyMember
    admins = FamilyMember.objects.filter(
        family=provider.family, role='admin', is_active=True
    )
    for admin in admins:
        channels = NotificationChannel.objects.filter(user=admin.user, is_enabled=True)
        for channel in channels:
            send_notification(
                channel,
                'Error de sincronizacion',
                f'Error sync {provider.provider_type}: {error_msg[:200]}',
                'sync_error',
            )
