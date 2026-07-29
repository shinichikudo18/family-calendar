import logging
from abc import ABC, abstractmethod
from django.utils import timezone
from events.models import Calendar, Event

logger = logging.getLogger(__name__)


class BaseSyncEngine(ABC):
    def __init__(self, provider):
        self.provider = provider
        self.family = provider.family

    @abstractmethod
    def fetch_events(self, since=None):
        pass

    @abstractmethod
    def push_event(self, event):
        pass

    @abstractmethod
    def update_event(self, event):
        pass

    @abstractmethod
    def delete_event(self, external_id):
        pass

    def import_events(self, calendar, since=None):
        from .models import SyncLog
        log = SyncLog.objects.create(provider=self.provider, status='running')
        imported = 0
        skipped = 0
        failed = 0
        try:
            external_events = self.fetch_events(since)
            for ext in external_events:
                try:
                    Event.objects.update_or_create(
                        calendar=calendar,
                        external_id=ext['external_id'],
                        external_provider=self.provider.provider_type,
                        defaults={
                            'title': ext['title'],
                            'description': ext.get('description', ''),
                            'start_time': ext['start_time'],
                            'end_time': ext['end_time'],
                            'all_day': ext.get('all_day', False),
                            'location': ext.get('location', ''),
                        }
                    )
                    imported += 1
                except Exception as e:
                    logger.warning(f'Failed to import event: {e}')
                    failed += 1
            log.status = 'success'
        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
        log.events_imported = imported
        log.events_skipped = skipped
        log.events_failed = failed
        log.completed_at = timezone.now()
        log.save()
        return log
