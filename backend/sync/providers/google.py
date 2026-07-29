import logging
from django.utils import timezone
from sync.engine import BaseSyncEngine

logger = logging.getLogger(__name__)


class GoogleCalendarEngine(BaseSyncEngine):
    def __init__(self, provider):
        super().__init__(provider)
        self.credentials = provider.credentials

    def _get_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials(token=self.credentials.get('access_token'),
                                refresh_token=self.credentials.get('refresh_token'),
                                token_uri='https://oauth2.googleapis.com/token',
                                client_id=self.credentials.get('client_id'),
                                client_secret=self.credentials.get('client_secret'))
            return build('calendar', 'v3', credentials=creds)
        except ImportError:
            logger.error('google-api-python-client not installed')
            return None

    def fetch_events(self, since=None):
        service = self._get_service()
        if not service:
            return []
        try:
            params = {'calendarId': 'primary', 'maxResults': 100, 'singleEvents': True, 'orderBy': 'startTime'}
            if since:
                params['timeMin'] = since.isoformat()
            events_result = service.events().list(**params).execute()
            events = []
            for item in events_result.get('items', []):
                start = item['start'].get('dateTime', item['start'].get('date'))
                end = item['end'].get('dateTime', item['end'].get('date'))
                events.append({
                    'external_id': f'google::{item[id]}',
                    'title': item.get('summary', ''),
                    'description': item.get('description', ''),
                    'start_time': start,
                    'end_time': end,
                    'all_day': 'date' in item['start'],
                    'location': item.get('location', ''),
                })
            return events
        except Exception as e:
            logger.error(f'Google API error: {e}')
            return []

    def push_event(self, event):
        raise NotImplementedError('Export not supported in IMPORT_ONLY mode')

    def update_event(self, event):
        raise NotImplementedError('Export not supported in IMPORT_ONLY mode')

    def delete_event(self, external_id):
        raise NotImplementedError('Export not supported in IMPORT_ONLY mode')
