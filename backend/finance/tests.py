import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from businesses.models import Business
from businesses.services import ensure_default_business
from cashflow.models import CashEntry
from cashflow.selectors import cash_entries_for_business
from expenses.models import Expense
from expenses.selectors import expenses_for_business
from expenses.serializers import validate_expense_payload
from expenses.services import create_expense
from inventory.models import InventoryItem, StockMovement
from inventory.selectors import inventory_for_business
from inventory.services import create_inventory_item
from reports.calculations import dashboard_for_business
from sales.models import Sale, SaleLine
from sales.selectors import sale_lines_for_business, sales_for_business
from sales.serializers import validate_sale_payload
from sales.services import create_sale, void_sale
from expenses.services import void_expense
from inventory.services import void_inventory_item


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
        payload = response.json()
        self.assertEqual(payload['user']['email'], 'amina@example.com')
        self.assertTrue(User.objects.filter(username='amina@example.com').exists())

        me_response = self.client.get('/api/auth/me/', HTTP_AUTHORIZATION=f"Bearer {payload['tokens']['access']}")
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
        self.assertIn('cashPosition', payload['summary'])
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

    def test_create_and_delete_sale_voids_record(self):
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
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(Sale.objects.get(id=sale_id).status, 'voided')
        self.assertEqual(self.client.get('/api/sales/').json()['sales'], [])

    def test_requires_auth_for_private_endpoints(self):
        response = self.client.get('/api/dashboard/')

        self.assertEqual(response.status_code, 401)

    def test_capital_withdrawal_rejects_capital_erosion(self):
        user = User.objects.create_user(username='amina@example.com', email='amina@example.com', password='secret123')
        business = ensure_default_business(user)
        self.client.login(username='amina@example.com', password='secret123')

        response = self.post_json(f'/api/businesses/{business.id}/capital/', {
            'entryType': 'owner_withdrawal',
            'amount': '1000',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('erode capital', response.json()['message'])


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
        self.assertEqual(payload['amount_paid'], Decimal('2500.00'))
        self.assertEqual(payload['payment_status'], 'paid')
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
                'inventory_item_id': None,
                'item_name': 'Onions',
                'amount': Decimal('3500.00'),
                'amount_paid': Decimal('3500.00'),
                'payment_status': 'paid',
                'quantity': 2,
                'note': '',
            },
        )

        self.assertEqual(sale.business, self.business)
        self.assertEqual(sales_for_business(self.business).count(), 1)
        self.assertEqual(SaleLine.objects.filter(sale=sale).count(), 1)
        self.assertEqual(CashEntry.objects.filter(reference_type='sale', reference_id=sale.id).count(), 1)

    def test_validate_sale_payload_supports_partial_payment(self):
        payload = validate_sale_payload({
            'itemName': 'Tomatoes',
            'amount': '5000',
            'amountPaid': '2000',
            'quantity': '2',
        })

        self.assertEqual(payload['amount_paid'], Decimal('2000.00'))
        self.assertEqual(payload['payment_status'], 'partial')

    def test_unpaid_expense_does_not_create_cash_entry(self):
        payload = validate_expense_payload({
            'category': 'Transport',
            'amount': '1200',
            'paymentStatus': 'unpaid',
        })

        expense = create_expense(business=self.business, payload=payload)

        self.assertEqual(expense.payment_status, 'unpaid')
        self.assertEqual(CashEntry.objects.filter(reference_type='expense', reference_id=expense.id).count(), 0)

    def test_void_sale_restores_stock_and_records_reversal(self):
        item = InventoryItem.objects.create(
            business=self.business,
            name='Tomatoes',
            quantity=10,
            unit_cost=Decimal('800.00'),
        )
        sale = create_sale(
            business=self.business,
            user=self.user,
            payload={
                'inventory_item_id': item.id,
                'item_name': 'Tomatoes',
                'amount': Decimal('3000.00'),
                'amount_paid': Decimal('3000.00'),
                'payment_status': 'paid',
                'quantity': 3,
                'note': '',
            },
        )

        self.assertTrue(void_sale(business=self.business, pk=sale.id, user=self.user, reason='Wrong sale'))

        item.refresh_from_db()
        sale.refresh_from_db()
        self.assertEqual(item.quantity, 10)
        self.assertEqual(sale.status, 'voided')
        self.assertEqual(sale.void_reason, 'Wrong sale')
        self.assertTrue(CashEntry.objects.filter(reference_type='sale_void', reference_id=sale.id).exists())

    def test_void_expense_records_cash_reversal(self):
        expense = create_expense(
            business=self.business,
            user=self.user,
            payload={
                'category': 'Transport',
                'expense_type': 'operating',
                'amount': Decimal('1200.00'),
                'payment_status': 'paid',
                'note': '',
            },
        )

        self.assertTrue(void_expense(business=self.business, pk=expense.id, user=self.user, reason='Duplicate'))

        expense.refresh_from_db()
        self.assertEqual(expense.status, 'voided')
        self.assertTrue(CashEntry.objects.filter(reference_type='expense_void', reference_id=expense.id).exists())

    def test_void_inventory_item_hides_item(self):
        item = create_inventory_item(
            business=self.business,
            user=self.user,
            payload={
                'name': 'Pepper',
                'quantity': 4,
                'unit': 'basket',
                'reorder_level': 1,
                'unit_cost': Decimal('1500.00'),
            },
        )

        self.assertTrue(void_inventory_item(business=self.business, pk=item.id, user=self.user, reason='Bad entry'))

        item.refresh_from_db()
        self.assertEqual(item.status, 'voided')
        self.assertEqual(list(inventory_for_business(self.business)), [])

    def test_create_sale_service_reduces_inventory_and_records_movement(self):
        item = InventoryItem.objects.create(
            business=self.business,
            name='Tomatoes',
            quantity=10,
            unit_cost=Decimal('800.00'),
        )

        sale = create_sale(
            business=self.business,
            payload={
                'inventory_item_id': item.id,
                'item_name': 'Tomatoes',
                'amount': Decimal('3000.00'),
                'amount_paid': Decimal('3000.00'),
                'payment_status': 'paid',
                'quantity': 3,
                'note': '',
            },
        )

        item.refresh_from_db()
        line = SaleLine.objects.get(sale=sale)
        movement = StockMovement.objects.get(reference_id=line.id)
        self.assertEqual(item.quantity, 7)
        self.assertEqual(line.inventory_item, item)
        self.assertEqual(line.unit_cost, Decimal('800.00'))
        self.assertEqual(movement.quantity_change, -3)
        self.assertEqual(movement.movement_type, 'sale')

    def test_create_sale_service_rejects_insufficient_stock(self):
        item = InventoryItem.objects.create(
            business=self.business,
            name='Tomatoes',
            quantity=1,
            unit_cost=Decimal('800.00'),
        )

        with self.assertRaises(ValueError):
            create_sale(
                business=self.business,
                payload={
                    'inventory_item_id': item.id,
                    'item_name': 'Tomatoes',
                    'amount': Decimal('3000.00'),
                    'amount_paid': Decimal('3000.00'),
                    'payment_status': 'paid',
                    'quantity': 3,
                    'note': '',
                },
            )

    def test_create_inventory_item_records_purchase_outflow(self):
        item = create_inventory_item(
            business=self.business,
            payload={
                'name': 'Pepper',
                'quantity': 4,
                'unit': 'basket',
                'reorder_level': 1,
                'unit_cost': Decimal('1500.00'),
            },
        )

        entry = CashEntry.objects.get(reference_type='inventory_item', reference_id=item.id)
        self.assertEqual(entry.direction, 'outflow')
        self.assertEqual(entry.amount, Decimal('6000.00'))

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
            sale_lines=sale_lines_for_business(self.business),
            cash_entries=cash_entries_for_business(self.business),
        )

        self.assertEqual(dashboard['summary']['costOfGoodsSold'], '0.00')
        self.assertEqual(dashboard['summary']['grossProfit'], '5000.00')
        self.assertEqual(dashboard['summary']['netProfit'], '3800.00')
        self.assertEqual(dashboard['summary']['cashPosition'], '0.00')
        self.assertEqual(dashboard['summary']['inventoryValue'], '2000.00')
        self.assertEqual(dashboard['lowStock'][0]['name'], 'Pepper')
