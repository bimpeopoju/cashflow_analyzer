import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from businesses.models import Business, BusinessMembership

from .models import OAuthIdentity


User = get_user_model()


class AuthenticationApiTests(TestCase):
    def post_json(self, path, payload):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def register(self):
        return self.post_json('/api/v1/auth/register/', {
            'fullName': 'Amina Musa',
            'email': 'Amina@Example.com',
            'password': 'Strong-pass-493!',
        })

    def test_register_normalizes_email_and_returns_token_pair(self):
        response = self.register()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user']['email'], 'amina@example.com')
        self.assertIn('access', response.json()['tokens'])
        self.assertIn('refresh', response.json()['tokens'])
        self.assertTrue(User.objects.filter(username='amina@example.com').exists())
        self.assertTrue(Business.objects.filter(owner__username='amina@example.com').exists())
        self.assertTrue(
            BusinessMembership.objects.filter(
                user__username='amina@example.com',
                role='owner',
                status='active',
            ).exists(),
        )

    def test_register_rejects_duplicate_email(self):
        self.register()

        response = self.register()

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_register_applies_django_password_validation(self):
        response = self.post_json('/api/v1/auth/register/', {
            'fullName': 'Amina Musa',
            'email': 'amina@example.com',
            'password': '123',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json())

    def test_login_returns_tokens_for_valid_credentials(self):
        self.register()
        self.client.logout()

        response = self.post_json('/api/v1/auth/login/', {
            'email': 'AMINA@example.com',
            'password': 'Strong-pass-493!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json()['tokens'])
        self.assertIn('refresh', response.json()['tokens'])

    def test_login_rejects_invalid_credentials(self):
        User.objects.create_user(
            username='amina@example.com',
            email='amina@example.com',
            password='Strong-pass-493!',
        )

        response = self.post_json('/api/v1/auth/login/', {
            'email': 'amina@example.com',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 401)

    def test_bearer_token_authenticates_me_and_legacy_finance_endpoint(self):
        registration = self.register().json()
        self.client.logout()
        authorization = f"Bearer {registration['tokens']['access']}"

        me_response = self.client.get('/api/v1/auth/me/', HTTP_AUTHORIZATION=authorization)
        dashboard_response = self.client.get('/api/dashboard/', HTTP_AUTHORIZATION=authorization)

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(dashboard_response.status_code, 200)

    def test_refresh_rotates_and_blacklists_previous_token(self):
        refresh = self.register().json()['tokens']['refresh']

        response = self.post_json('/api/v1/auth/refresh/', {'refresh': refresh})

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
        self.assertEqual(BlacklistedToken.objects.count(), 1)

    def test_logout_blacklists_refresh_token(self):
        refresh = self.register().json()['tokens']['refresh']

        response = self.post_json('/api/v1/auth/logout/', {'refresh': refresh})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(BlacklistedToken.objects.count(), 1)

    def test_legacy_auth_route_remains_available(self):
        response = self.post_json('/api/auth/register/', {
            'fullName': 'Amina Musa',
            'email': 'amina@example.com',
            'password': 'Strong-pass-493!',
        })

        self.assertEqual(response.status_code, 201)

    def test_oauth_provider_discovery_exposes_disabled_google_scaffold(self):
        response = self.client.get('/api/v1/auth/oauth/providers/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['providers'][0]['id'], 'google')
        self.assertFalse(response.json()['providers'][0]['enabled'])


class OAuthIdentityTests(TestCase):
    def test_provider_subject_is_unique(self):
        first = User.objects.create_user(username='first@example.com')
        second = User.objects.create_user(username='second@example.com')
        OAuthIdentity.objects.create(user=first, provider='google', subject='provider-user-1')

        with self.assertRaises(IntegrityError), transaction.atomic():
            OAuthIdentity.objects.create(
                user=second,
                provider='google',
                subject='provider-user-1',
            )

    def test_user_can_link_only_one_identity_per_provider(self):
        user = User.objects.create_user(username='amina@example.com')
        OAuthIdentity.objects.create(user=user, provider='google', subject='provider-user-1')

        with self.assertRaises(IntegrityError), transaction.atomic():
            OAuthIdentity.objects.create(
                user=user,
                provider='google',
                subject='provider-user-2',
            )
