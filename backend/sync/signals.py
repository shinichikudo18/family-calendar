import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SyncProvider
from .providers import PROVIDERS
from .tasks import run_sync

logger = logging.getLogger(__name__)


def get_bidirectional_providers(family_id):
    return SyncProvider.objects.filter(
        family_id=family_id, is_enabled=True,
        sync_mode__in=['export', 'bidirectional'],
    )


@receiver(post_save, sender='events.Event')
def event_saved(sender, instance, created, **kwargs):
    if instance.external_provider:
        return
    if instance.is_proposal:
        return
    providers = get_bidirectional_providers(instance.calendar.family_id)
    for provider in providers:
        try:
            engine = PROVIDERS[provider.provider_type](provider)
            if created:
                engine.push_event(instance)
            else:
                if not instance.is_cancelled:
                    engine.update_event(instance)
        except Exception as e:
            logger.warning(f'Bidirectional sync failed for {provider}: {e}')


@receiver(post_delete, sender='events.Event')
def event_deleted(sender, instance, **kwargs):
    if instance.external_id:
        providers = get_bidirectional_providers(instance.calendar.family_id)
        for provider in providers:
            try:
                engine = PROVIDERS[provider.provider_type](provider)
                engine.delete_event(instance.external_id)
            except Exception as e:
                logger.warning(f'Delete sync failed for {provider}: {e}')
