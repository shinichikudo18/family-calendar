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
