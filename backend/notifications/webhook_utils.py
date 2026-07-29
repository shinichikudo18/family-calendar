import hmac
import hashlib
import time
import json
import logging
import requests
from django.conf import settings
from .models import WebhookEndpoint, WebhookDelivery

logger = logging.getLogger(__name__)

MAX_TIMESTAMP_AGE = 300


def sign_payload(payload: dict, secret: str) -> tuple[str, str, str]:
    timestamp = str(int(time.time()))
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    message = f'{timestamp}.{raw}'.encode()
    signature = hmac.new(
        secret.encode(), message, hashlib.sha256
    ).hexdigest()
    return signature, timestamp, raw


def verify_signature(
    payload_raw: str, signature: str, timestamp: str, secret: str
) -> bool:
    try:
        ts = int(timestamp)
        now = int(time.time())
        if abs(now - ts) > MAX_TIMESTAMP_AGE:
            return False
        message = f'{timestamp}.{payload_raw}'.encode()
        expected = hmac.new(
            secret.encode(), message, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except (ValueError, TypeError):
        return False


def deliver_webhook(endpoint: WebhookEndpoint, event_type: str, payload: dict):
    from django.utils import timezone
    secret = endpoint.get_signing_secret()
    if not secret:
        logger.error(f'No signing secret for endpoint {endpoint.id}')
        return

    signature, timestamp, raw = sign_payload(payload, secret)
    payload_hash = hashlib.sha256(raw.encode()).hexdigest()

    delivery = WebhookDelivery.objects.create(
        endpoint=endpoint,
        event_type=event_type,
        payload_hash=payload_hash,
        status='pending',
    )

    headers = {
        'Content-Type': 'application/json',
        'X-FamilyCalendar-Signature': signature,
        'X-FamilyCalendar-Timestamp': timestamp,
        'X-FamilyCalendar-Event': event_type,
        'User-Agent': 'FamilyCalendar-Webhook/1.0',
    }

    try:
        resp = requests.post(
            endpoint.target_url,
            data=raw,
            headers=headers,
            timeout=30,
        )
        delivery.response_status = resp.status_code
        if 200 <= resp.status_code < 300:
            delivery.status = 'success'
            delivery.delivered_at = timezone.now()
            endpoint.last_success_at = timezone.now()
        else:
            delivery.status = 'failed'
            endpoint.last_error_at = timezone.now()
    except requests.RequestException as e:
        logger.warning(f'Webhook delivery failed: {e}')
        delivery.status = 'failed'
        endpoint.last_error_at = timezone.now()

    delivery.attempts += 1
    delivery.save()
    endpoint.save()
    return delivery


def retry_failed_deliveries(max_retries: int = 5):
    from django.utils import timezone
    deliveries = WebhookDelivery.objects.filter(
        status='failed', attempts__lt=max_retries
    )[:50]

    for delivery in deliveries:
        delivery.status = 'retrying'
        delivery.save()
        endpoint = delivery.endpoint
        if not endpoint.is_enabled:
            continue
        payload = {'event_type': delivery.event_type}
        new_delivery = deliver_webhook(endpoint, delivery.event_type, payload)
        if new_delivery and new_delivery.status == 'success':
            delivery.delete()
