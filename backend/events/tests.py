import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from accounts.models import Family, FamilyMember
from .models import Calendar, Event, EventParticipant


@pytest.mark.django_db
class TestCalendar:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user('caluser', 'c@t.com', 'Test12345!')
        self.family = Family.objects.create(name='Test Fam', created_by=self.user)
        FamilyMember.objects.create(family=self.family, user=self.user, role='admin')
        resp = self.client.post('/api/v1/auth/login/', {
            'username': 'caluser', 'password': 'Test12345!'
        })
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_calendar(self):
        resp = self.client.post('/api/v1/events/calendars/', {
            'family': str(self.family.id), 'name': 'Mi Calendario', 'color': '#FF0000'
        })
        assert resp.status_code == 201
        assert resp.data['name'] == 'Mi Calendario'

    def test_create_event(self):
        cal = Calendar.objects.create(
            family=self.family, name='Test', created_by=self.user
        )
        resp = self.client.post('/api/v1/events/events/', {
            'calendar': str(cal.id), 'title': 'Evento Test',
            'start_time': '2026-07-29T10:00:00Z',
            'end_time': '2026-07-29T11:00:00Z',
        })
        assert resp.status_code == 201
        assert resp.data['title'] == 'Evento Test'

    def test_list_events_date_range(self):
        cal = Calendar.objects.create(
            family=self.family, name='Test', created_by=self.user
        )
        Event.objects.create(
            calendar=cal, title='Event 1',
            start_time='2026-07-29T10:00:00Z', end_time='2026-07-29T11:00:00Z',
            created_by=self.user
        )
        resp = self.client.get(
            '/api/v1/events/events/?from=2026-07-01T00:00:00Z&to=2026-07-31T23:59:59Z'
        )
        assert resp.status_code == 200
        assert resp.data['count'] == 1

    def test_cancel_event(self):
        cal = Calendar.objects.create(
            family=self.family, name='Test', created_by=self.user
        )
        event = Event.objects.create(
            calendar=cal, title='To Cancel',
            start_time='2026-07-29T10:00:00Z', end_time='2026-07-29T11:00:00Z',
            created_by=self.user
        )
        resp = self.client.post(f'/api/v1/events/events/{event.id}/cancel/')
        assert resp.status_code == 200
        event.refresh_from_db()
        assert event.is_cancelled is True

    def test_today_events(self):
        cal = Calendar.objects.create(
            family=self.family, name='Test', created_by=self.user
        )
        Event.objects.create(
            calendar=cal, title='Today Event',
            start_time='2026-07-28T10:00:00Z', end_time='2026-07-28T11:00:00Z',
            created_by=self.user
        )
        resp = self.client.get('/api/v1/events/events/today/')
        assert resp.status_code == 200

    def test_upcoming_events(self):
        cal = Calendar.objects.create(
            family=self.family, name='Test', created_by=self.user
        )
        Event.objects.create(
            calendar=cal, title='Future Event',
            start_time='2099-01-01T10:00:00Z', end_time='2099-01-01T11:00:00Z',
            created_by=self.user
        )
        resp = self.client.get('/api/v1/events/events/upcoming/')
        assert resp.status_code == 200
        assert len(resp.data) == 1
