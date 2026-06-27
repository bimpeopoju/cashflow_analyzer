from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from businesses.services import ensure_default_business
from cashflow.selectors import cash_entries_for_business
from expenses.models import Expense
from expenses.selectors import expenses_for_business
from expenses.services import create_expense
from forecasting.calculations import ForecastDataUnavailable, forecast_for_business
from forecasting.models import ForecastPeriod, ForecastRun
from sales.models import SaleLine
from sales.selectors import sale_lines_for_business, sales_for_business
from sales.services import create_sale


User = get_user_model()


class ForecastCalculationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='amina@example.com',
            email='amina@example.com',
            password='secret123',
        )
        self.business = ensure_default_business(self.user)

    def test_forecast_rejects_empty_business(self):
        with self.assertRaises(ForecastDataUnavailable):
            forecast_for_business(
                business=self.business,
                sales=sales_for_business(self.business),
                expenses=expenses_for_business(self.business),
                sale_lines=sale_lines_for_business(self.business),
                cash_entries=cash_entries_for_business(self.business),
            )

    def test_forecast_projects_from_historical_transactions(self):
        for amount in [Decimal('10000.00'), Decimal('12000.00'), Decimal('14000.00')]:
            sale = create_sale(
                business=self.business,
                payload={
                    'inventory_item_id': None,
                    'item_name': 'Tomatoes',
                    'amount': amount,
                    'amount_paid': amount,
                    'payment_status': 'paid',
                    'quantity': 10,
                    'note': '',
                },
            )
            SaleLine.objects.filter(sale=sale).update(unit_cost=Decimal('400.00'))
        create_expense(
            business=self.business,
            payload={
                'category': 'Transport',
                'amount': Decimal('3000.00'),
                'expense_type': Expense.TYPE_OPERATING,
                'payment_status': Expense.PAYMENT_PAID,
                'note': '',
            },
        )

        result = forecast_for_business(
            business=self.business,
            sales=sales_for_business(self.business),
            expenses=expenses_for_business(self.business),
            sale_lines=sale_lines_for_business(self.business),
            cash_entries=cash_entries_for_business(self.business),
            lookback_days=7,
            horizon_days=7,
        )

        self.assertIsNone(result['id'])
        self.assertEqual(result['horizonDays'], 7)
        self.assertEqual(len(result['periods']), 7)
        self.assertGreater(Decimal(result['summary']['projectedSales']), Decimal('0.00'))
        self.assertIn(result['confidence'], ['low', 'medium', 'high'])

    def test_forecast_can_persist_run_and_periods(self):
        sale = create_sale(
            business=self.business,
            payload={
                'inventory_item_id': None,
                'item_name': 'Tomatoes',
                'amount': Decimal('7000.00'),
                'amount_paid': Decimal('7000.00'),
                'payment_status': 'paid',
                'quantity': 7,
                'note': '',
            },
        )
        SaleLine.objects.filter(sale=sale).update(unit_cost=Decimal('300.00'))

        result = forecast_for_business(
            business=self.business,
            sales=sales_for_business(self.business),
            expenses=expenses_for_business(self.business),
            sale_lines=sale_lines_for_business(self.business),
            cash_entries=cash_entries_for_business(self.business),
            lookback_days=7,
            horizon_days=7,
            persist=True,
            user=self.user,
        )

        self.assertIsNotNone(result['id'])
        self.assertEqual(ForecastRun.objects.count(), 1)
        self.assertEqual(ForecastPeriod.objects.count(), 7)


class ForecastApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='amina@example.com',
            email='amina@example.com',
            password='secret123',
        )
        self.business = ensure_default_business(self.user)
        self.client.login(username='amina@example.com', password='secret123')

    def add_sale(self):
        sale = create_sale(
            business=self.business,
            payload={
                'inventory_item_id': None,
                'item_name': 'Tomatoes',
                'amount': Decimal('10000.00'),
                'amount_paid': Decimal('10000.00'),
                'payment_status': 'paid',
                'quantity': 10,
                'note': '',
            },
        )
        SaleLine.objects.filter(sale=sale).update(unit_cost=Decimal('400.00'))

    def test_forecast_preview_does_not_persist(self):
        self.add_sale()

        response = self.client.get(f'/api/businesses/{self.business.id}/forecasts/?lookbackDays=7&horizonDays=7')

        self.assertEqual(response.status_code, 200)
        payload = response.json()['forecast']
        self.assertIsNone(payload['id'])
        self.assertEqual(len(payload['periods']), 7)
        self.assertEqual(ForecastRun.objects.count(), 0)

    def test_forecast_post_persists_run(self):
        self.add_sale()

        response = self.client.post(f'/api/businesses/{self.business.id}/forecasts/?lookbackDays=7&horizonDays=7')

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json()['forecast']['id'])
        self.assertEqual(ForecastRun.objects.count(), 1)
        self.assertEqual(ForecastPeriod.objects.count(), 7)

    def test_forecast_requires_transactions(self):
        response = self.client.get(f'/api/businesses/{self.business.id}/forecasts/')

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['code'], 'forecast_data_unavailable')

    def test_forecast_rejects_unrelated_business(self):
        other = User.objects.create_user(username='other@example.com', email='other@example.com', password='secret123')
        other_business = ensure_default_business(other)

        response = self.client.get(f'/api/businesses/{other_business.id}/forecasts/')

        self.assertEqual(response.status_code, 404)
