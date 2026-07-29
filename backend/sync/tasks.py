import logging
from celery import shared_task
from django.utils import timezone
from .models import SyncProvider
from .providers import PROVIDERS

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def run_sync(self, provider_id):
    try:
        provider = SyncProvider.objects.get(id=provider_id, is_enabled=True)
    except SyncProvider.DoesNotExist:
        logger.error(f'SyncProvider {provider_id} not found')
        return False

    engine_class = PROVIDERS.get(provider.provider_type)
    if not engine_class:
        logger.error(f'No engine for {provider.provider_type}')
        return False

    engine = engine_class(provider)
    cal = provider.family.calendars.first()
    if not cal:
        logger.warning(f'No calendar for family {provider.family}')
        return False

    log = engine.import_events(cal, since=provider.last_sync_at or (timezone.now() - timezone.timedelta(days=7)))
    provider.last_sync_at = timezone.now()
    provider.save()

    if log.status == 'failed':
        raise self.retry(exc=Exception(log.error_message))
    return True


@shared_task
def sync_all_providers():
    providers = SyncProvider.objects.filter(is_enabled=True)
    for provider in providers:
        run_sync.delay(str(provider.id))
