import logging
from celery import shared_task
from django.utils import timezone
from .models import WebhookDelivery
from .webhook_utils import deliver_webhook, retry_failed_deliveries

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_webhook_notification(self, endpoint_id, event_type, payload):
    from .models import WebhookEndpoint
    try:
        endpoint = WebhookEndpoint.objects.get(id=endpoint_id, is_enabled=True)
    except WebhookEndpoint.DoesNotExist:
        logger.error(f'WebhookEndpoint {endpoint_id} not found or disabled')
        return False

    delivery = deliver_webhook(endpoint, event_type, payload)
    if delivery and delivery.status == 'failed':
        raise self.retry(exc=Exception(f'Delivery failed: {delivery.response_status}'))
    return True


@shared_task
def cleanup_old_deliveries(days=30):
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = WebhookDelivery.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f'Cleaned up {deleted} old webhook deliveries')
    return deleted


@shared_task
def retry_webhooks():
    retry_failed_deliveries()

@shared_task
def send_event_reminders():
    from django.utils import timezone
    from events.models import Event
    from .models import NotificationRule
    now = timezone.now()
    rules = NotificationRule.objects.filter(
        event_type='event_reminder', is_enabled=True
    ).select_related('channel__user')
    processed = set()
    for rule in rules:
        remind_at = now + timezone.timedelta(minutes=rule.minutes_before)
        window_end = remind_at + timezone.timedelta(minutes=1)
        events = Event.objects.filter(
            start_time__gte=remind_at, start_time__lte=window_end,
            is_cancelled=False, is_proposal=False,
        )
        for event in events:
            key = (event.id, rule.channel.user_id)
            if key in processed:
                continue
            processed.add(key)
            from .services import send_notification
            send_notification(
                rule.channel,
                f'Recordatorio: {event.title}',
                f'Comienza en {rule.minutes_before} minutos:\n{event.title}',
                'event_reminder',
            )


@shared_task
def send_daily_summaries():
    from django.utils import timezone
    from events.models import Event
    from .models import NotificationRule, NotificationChannel
    from .services import send_daily_summary
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timezone.timedelta(days=1)
    rules = NotificationRule.objects.filter(
        event_type='daily_summary', is_enabled=True
    ).select_related('channel__user')
    for rule in rules:
        events = Event.objects.filter(
            start_time__gte=today_start, start_time__lt=today_end,
            is_cancelled=False, is_proposal=False,
        ).order_by('start_time')[:20]
        send_daily_summary(rule.channel.user, list(events))


@shared_task
def retry_webhooks():
    retry_failed_deliveries()
