import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .calculations import dashboard_for_business
from .models import Business, Expense, InventoryItem, Sale
from .selectors import expenses_for_business, inventory_for_business, sales_for_business
from .serializers import validate_sale_payload
from .services import create_sale, ensure_default_business


User = get_user_model()


class FinanceApiTests(TestCase):
    def post_json(self, path, payload):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_register_logs_user_in(self):
        response = self.post_json('/api/auth/register/', {
            'fullName': 'Amina Musa',
            'email': 'amina@example.com',
            'password': 'Strong-pass-493!',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user']['email'], 'amina@example.com')
        self.assertTrue(User.objects.filter(username='amina@example.com').exists())

        me_response = self.client.get('/api/auth/me/')
        self.assertEqual(me_response.status_code, 200)

    def test_login_rejects_bad_credentials(self):
        User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')

        response = self.post_json('/api/auth/login/', {
            'email': 'amina@example.com',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 401)

    def test_dashboard_summarizes_user_owned_records(self):
        user = User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        other = User.objects.create_user(username='other@example.com', email='other@example.com', password='secret123')
        business = ensure_default_business(user)
        other_business = ensure_default_business(other)
        self.client.login(username='amina@example.com', password='secret123')

        Sale.objects.create(business=business, item_name='Tomatoes', amount=Decimal('5000.00'), quantity=3)
        Expense.objects.create(business=business, category='Transport', amount=Decimal('1200.00'))
        InventoryItem.objects.create(business=business, name='Pepper', quantity=2, reorder_level=5, unit_cost=Decimal('1000.00'))
        Sale.objects.create(business=other_business, item_name='Hidden', amount=Decimal('999999.00'), quantity=1)

        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['salesToday'], '5000.00')
        self.assertEqual(payload['summary']['expensesToday'], '1200.00')
        self.assertEqual(payload['summary']['netProfit'], '3800.00')
        self.assertEqual(payload['lowStock'][0]['name'], 'Pepper')

    def test_business_scoped_dashboard_rejects_unrelated_business(self):
        User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        other = User.objects.create_user(username='other@example.com', email='other@example.com', password='secret123')
        other_business = ensure_default_business(other)
        self.client.login(username='amina@example.com', password='secret123')

        response = self.client.get(f'/api/businesses/{other_business.id}/dashboard/')

        self.assertEqual(response.status_code, 404)

    def test_business_list_returns_user_memberships(self):
        User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        self.client.login(username='amina@example.com', password='secret123')

        response = self.client.get('/api/businesses/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['businesses']), 1)
        self.assertEqual(response.json()['businesses'][0]['role'], 'owner')

    def test_create_business(self):
        User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        self.client.login(username='amina@example.com', password='secret123')

        response = self.post_json('/api/businesses/', {
            'name': 'Second Stall',
            'stallName': 'Line B',
            'initialCapital': '50000',
        })

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Business.objects.filter(name='Second Stall').exists())

    def test_create_and_delete_sale(self):
        User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        self.client.login(username='amina@example.com', password='secret123')

        create_response = self.post_json('/api/sales/', {
            'itemName': 'Onions',
            'amount': '3500',
            'quantity': 2,
        })
        sale_id = create_response.json()['sale']['id']

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(Sale.objects.count(), 1)

        delete_response = self.client.delete(f'/api/sales/{sale_id}/')

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(Sale.objects.count(), 0)

    def test_requires_auth_for_private_endpoints(self):
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, 401)


class FinanceServiceLayerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='amina@example.com',
            email='amina@example.com',
            password='secret123',
        )
        self.business = ensure_default_business(self.user)

    def test_validate_sale_payload_normalizes_fields(self):
        payload = validate_sale_payload({
            'itemName': ' Tomatoes ',
            'amount': '2500',
            'quantity': '2',
            'note': ' morning sales ',
        })

        self.assertEqual(payload['item_name'], 'Tomatoes')
        self.assertEqual(payload['amount'], Decimal('2500.00'))
        self.assertEqual(payload['quantity'], 2)
        self.assertEqual(payload['note'], 'morning sales')

    def test_validate_sale_payload_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            validate_sale_payload({
                'itemName': 'Tomatoes',
                'amount': '-1',
                'quantity': 1,
            })

    def test_create_sale_service_scopes_to_business(self):
        sale = create_sale(
            business=self.business,
            payload={
                'item_name': 'Onions',
                'amount': Decimal('3500.00'),
                'quantity': 2,
                'note': '',
            },
        )

        self.assertEqual(sale.business, self.business)
        self.assertEqual(sales_for_business(self.business).count(), 1)

    def test_dashboard_calculation_uses_supplied_business_querysets(self):
        Sale.objects.create(business=self.business, item_name='Tomatoes', amount=Decimal('5000.00'), quantity=3)
        Expense.objects.create(business=self.business, category='Transport', amount=Decimal('1200.00'))
        InventoryItem.objects.create(
            business=self.business,
            name='Pepper',
            quantity=2,
            reorder_level=5,
            unit_cost=Decimal('1000.00'),
        )

        dashboard = dashboard_for_business(
            business=self.business,
            sales=sales_for_business(self.business),
            expenses=expenses_for_business(self.business),
            inventory=inventory_for_business(self.business),
        )

        self.assertEqual(dashboard['summary']['netProfit'], '3800.00')
        self.assertEqual(dashboard['summary']['inventoryValue'], '2000.00')
        self.assertEqual(dashboard['lowStock'][0]['name'], 'Pepper')
