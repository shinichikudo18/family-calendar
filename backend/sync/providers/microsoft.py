import logging
from sync.engine import BaseSyncEngine

logger = logging.getLogger(__name__)


class MicrosoftCalendarEngine(BaseSyncEngine):
    def __init__(self, provider):
        super().__init__(provider)
        self.credentials = provider.credentials
        self.graph_base = "https://graph.microsoft.com/v1.0"

    def _get_headers(self):
        return {
            "Authorization": "Bearer " + self.credentials.get("access_token", ""),
            "Content-Type": "application/json",
        }

    def _is_token_expired(self):
        from django.utils import timezone
        expires_at = self.credentials.get("expires_at")
        if not expires_at:
            return True
        return timezone.now() >= timezone.datetime.fromisoformat(expires_at)

    def fetch_events(self, since=None):
        if self._is_token_expired():
            logger.warning("Microsoft token expired")
            return []
        import requests
        from datetime import timedelta
        dollar = chr(36)
        params = {dollar + "top": 100, dollar + "orderby": "start/dateTime", dollar + "select": "id,subject,bodyPreview,start,end,location,isAllDay"}
        url = self.graph_base + "/me/events"
        if since:
            url = self.graph_base + "/me/calendarview?startDateTime=" + since.isoformat() + "&endDateTime=" + (since + timedelta(days=30)).isoformat()
        resp = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        if resp.status_code != 200:
            logger.error("Microsoft API error: " + str(resp.status_code))
            return []
        events = []
        for item in resp.json().get("value", []):
            events.append({
                "external_id": "ms::" + item["id"],
                "title": item.get("subject", ""),
                "description": item.get("bodyPreview", ""),
                "start_time": item["start"]["dateTime"],
                "end_time": item["end"]["dateTime"],
                "all_day": item.get("isAllDay", False),
                "location": item.get("location", {}).get("displayName", ""),
            })
        return events

    def push_event(self, event):
        raise NotImplementedError("Export not supported in IMPORT_ONLY mode")

    def update_event(self, event):
        raise NotImplementedError("Export not supported in IMPORT_ONLY mode")

    def delete_event(self, external_id):
        raise NotImplementedError("Export not supported in IMPORT_ONLY mode")
