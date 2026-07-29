import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Family, FamilyMember


@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()

    def test_register_user(self):
        resp = self.client.post('/api/v1/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        })
        assert resp.status_code == 201
        assert resp.data['username'] == 'testuser'

    def test_register_with_invite_code(self):
        family = Family.objects.create(name='Test Family', created_by=None)
        resp = self.client.post('/api/v1/auth/register/', {
            'username': 'inviteduser',
            'email': 'invited@example.com',
            'password': 'TestPass123!',
            'invite_code': family.invite_code,
        })
        assert resp.status_code == 201
        assert FamilyMember.objects.filter(
            family=family, user__username='inviteduser'
        ).exists()

    def test_login(self):
        User.objects.create_user('loginuser', 'login@test.com', 'TestPass123!')
        resp = self.client.post('/api/v1/auth/login/', {
            'username': 'loginuser',
            'password': 'TestPass123!',
        })
        assert resp.status_code == 200
        assert 'access' in resp.data

    def test_profile_requires_auth(self):
        resp = self.client.get('/api/v1/auth/profile/')
        assert resp.status_code == 401


@pytest.mark.django_db
class TestFamily:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user('familyuser', 'f@test.com', 'TestPass123!')
        resp = self.client.post('/api/v1/auth/login/', {
            'username': 'familyuser', 'password': 'TestPass123!'
        })
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_family(self):
        resp = self.client.post('/api/v1/auth/families/', {'name': 'Mi Familia'})
        assert resp.status_code == 201
        assert resp.data['name'] == 'Mi Familia'
        assert Family.objects.count() == 1

    def test_create_family_makes_admin(self):
        resp = self.client.post('/api/v1/auth/families/', {'name': 'Admin Test'})
        family = Family.objects.get(id=resp.data['id'])
        assert FamilyMember.objects.filter(
            family=family, user=self.user, role='admin'
        ).exists()

    def test_join_family(self):
        family = Family.objects.create(name='Joinable', created_by=None)
        resp = self.client.post('/api/v1/auth/families/join/', {
            'invite_code': family.invite_code
        })
        assert resp.status_code == 200
        assert FamilyMember.objects.filter(
            family=family, user=self.user
        ).exists()

    def test_join_wrong_code(self):
        Family.objects.create(name='Secret', created_by=None)
        resp = self.client.post('/api/v1/auth/families/join/', {
            'invite_code': 'wrong-code'
        })
        assert resp.status_code == 404

    def test_list_my_families(self):
        family = Family.objects.create(name='My Fam', created_by=self.user)
        FamilyMember.objects.create(family=family, user=self.user, role='admin')
        resp = self.client.get('/api/v1/auth/families/')
        assert resp.status_code == 200
        assert len(resp.data) > 0
