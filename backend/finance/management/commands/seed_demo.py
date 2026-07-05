import random
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from businesses.models import Business
from businesses.services import create_business_for_user
from cashflow.models import CashEntry
from cashflow.selectors import cash_entries_for_business
from expenses.models import Expense
from expenses.selectors import expenses_for_business
from forecasting.calculations import forecast_for_business
from inventory.models import InventoryItem, StockMovement
from reports.selectors import sale_lines_for_business, sales_for_business
from sales.models import Sale, SaleLine
from taxes.calculations import estimate_tax_for_business


DEMO_EMAIL = 'demo.marketflow@example.com'
DEMO_PASSWORD = 'MarketFlowDemo2026!'


PRODUCTS = [
    ('Rice 5kg Bag', 'bags', 18, 8, '7200', '8900', 8),
    ('Brown Beans 2kg', 'bags', 20, 8, '3300', '4200', 6),
    ('Garri Ijebu 2kg', 'bags', 24, 10, '2400', '3100', 7),
    ('Golden Penny Semovita 1kg', 'packs', 22, 8, '1250', '1650', 6),
    ('Honeywell Wheat Meal 1kg', 'packs', 14, 6, '1350', '1750', 4),
    ('Golden Penny Spaghetti 500g', 'packs', 42, 15, '780', '1000', 9),
    ('Indomie Chicken Noodles', 'packs', 75, 25, '280', '400', 10),
    ('Dangote Sugar 1kg', 'packs', 26, 10, '1500', '1900', 7),
    ('Dangote Salt 500g', 'packs', 35, 12, '430', '600', 6),
    ('Kings Vegetable Oil 1L', 'bottles', 20, 8, '2500', '3200', 7),
    ('Power Oil 750ml', 'bottles', 16, 8, '2100', '2800', 6),
    ('Gino Tomato Paste 210g', 'tins', 45, 15, '650', '850', 8),
    ('Peak Milk Powder 400g', 'tins', 8, 12, '4200', '5200', 6),
    ('Dano Milk Powder 400g', 'tins', 14, 8, '3900', '4800', 5),
    ('Milo 400g', 'tins', 18, 8, '3100', '3900', 5),
    ('Bournvita 500g', 'jars', 15, 7, '3500', '4400', 4),
    ('Cabin Biscuit Family Pack', 'packs', 36, 12, '850', '1100', 6),
    ('Yale Chin Chin 500g', 'packs', 28, 10, '1500', '2000', 5),
    ('Gala Sausage Roll', 'packs', 48, 18, '320', '500', 8),
    ('Fresh Bread Large Loaf', 'loaves', 9, 10, '1200', '1600', 8),
    ('Crate of Eggs', 'crates', 4, 6, '5200', '6500', 5),
    ('Coca-Cola 50cl', 'bottles', 55, 20, '300', '500', 9),
    ('Bigi Water 75cl', 'bottles', 70, 24, '180', '300', 8),
    ('Hollandia Yoghurt 1L', 'cartons', 10, 5, '3200', '4000', 4),
    ('Geisha Bathing Soap', 'bars', 38, 12, '620', '850', 6),
    ('Eva Bathing Soap', 'bars', 30, 10, '700', '950', 5),
    ('Omo Detergent 900g', 'packs', 22, 8, '1900', '2500', 5),
    ('Sunlight Detergent 1kg', 'packs', 24, 8, '1850', '2400', 5),
    ('Morning Fresh 450ml', 'bottles', 18, 7, '1200', '1600', 4),
    ('Hypo Bleach 500ml', 'bottles', 30, 10, '600', '850', 5),
    ('Dettol Antiseptic 250ml', 'bottles', 16, 6, '1800', '2400', 4),
    ('Closeup Toothpaste 140g', 'tubes', 25, 9, '1200', '1600', 5),
    ('Oral-B Toothbrush', 'packs', 20, 7, '900', '1250', 3),
    ('Always Sanitary Pads', 'packs', 18, 8, '1500', '2000', 5),
    ('Pampers Size 4 Jumbo Pack', 'packs', 3, 5, '12500', '15000', 3),
    ('Huggies Baby Wipes', 'packs', 12, 6, '1800', '2400', 4),
]


def local_datetime(day, hour, minute=0):
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


class Command(BaseCommand):
    help = 'Create or reset a complete Nigerian grocery-store demo account.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default=DEMO_EMAIL)
        parser.add_argument('--password', default=DEMO_PASSWORD)

    @transaction.atomic
    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        rng = random.Random(20260701)
        today = timezone.localdate()
        first_day = today - timedelta(days=89)
        User = get_user_model()

        existing_user = User.objects.filter(username__iexact=email).first()
        if existing_user:
            Business.objects.filter(owner=existing_user).delete()
            existing_user.delete()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name='Amina',
            last_name='Okafor',
        )
        business = create_business_for_user(
            user=user,
            name='Amina Neighbourhood Mart',
            stall_name='Shop 14, Unity Market, Lagos',
            initial_capital=Decimal('5000000.00'),
        )
        business.tin = '20345678-0001'
        business.entity_type = Business.ENTITY_COMPANY
        business.vat_registered = True
        business.accounting_year_end_month = 12
        business.accounting_year_end_day = 31
        business.save(update_fields=[
            'tin',
            'entity_type',
            'vat_registered',
            'accounting_year_end_month',
            'accounting_year_end_day',
            'updated_at',
        ])

        inventory = [
            InventoryItem(
                business=business,
                name=name,
                unit=unit,
                quantity=current_quantity,
                reorder_level=reorder_level,
                unit_cost=Decimal(unit_cost),
                created_by=user,
            )
            for name, unit, current_quantity, reorder_level, unit_cost, _, _ in PRODUCTS
        ]
        InventoryItem.objects.bulk_create(inventory)

        prices = {item.name: Decimal(product[5]) for item, product in zip(inventory, PRODUCTS)}
        demand_weights = [product[6] for product in PRODUCTS]
        sold_quantities = {item.id: 0 for item in inventory}
        sales = []
        sale_dates = []

        for offset in range(90):
            day = first_day + timedelta(days=offset)
            base_transactions = 8 if day.weekday() in (4, 5) else 6
            transaction_count = base_transactions + rng.randint(0, 2)
            for sequence in range(transaction_count):
                item = rng.choices(inventory, weights=demand_weights, k=1)[0]
                quantity = rng.choices([1, 2, 3, 4], weights=[45, 30, 18, 7], k=1)[0]
                amount = prices[item.name] * quantity
                payment_roll = rng.random()
                if payment_roll < 0.91:
                    amount_paid = amount
                    payment_status = Sale.PAYMENT_PAID
                elif payment_roll < 0.97:
                    amount_paid = (amount * Decimal('0.60')).quantize(Decimal('0.01'))
                    payment_status = Sale.PAYMENT_PARTIAL
                else:
                    amount_paid = Decimal('0.00')
                    payment_status = Sale.PAYMENT_UNPAID

                sales.append(Sale(
                    business=business,
                    item_name=item.name,
                    amount=amount,
                    amount_paid=amount_paid,
                    payment_status=payment_status,
                    quantity=quantity,
                    note='Seeded demo grocery sale',
                    created_by=user,
                ))
                sale_dates.append(local_datetime(
                    day,
                    8 + ((sequence * 2 + rng.randint(0, 1)) % 12),
                    rng.choice([0, 10, 20, 30, 40, 50]),
                ))
                sold_quantities[item.id] += quantity

        Sale.objects.bulk_create(sales, batch_size=500)
        for sale, sold_at in zip(sales, sale_dates):
            sale.sold_at = sold_at
        Sale.objects.bulk_update(sales, ['sold_at'], batch_size=500)

        sale_lines = []
        sale_cash_entries = []
        sale_movements = []
        movement_dates = []
        for sale, sold_at in zip(sales, sale_dates):
            item = next(candidate for candidate in inventory if candidate.name == sale.item_name)
            sale_lines.append(SaleLine(
                sale=sale,
                inventory_item=item,
                item_name=item.name,
                quantity=sale.quantity,
                unit_price=prices[item.name],
                unit_cost=item.unit_cost,
                line_total=sale.amount,
            ))
            if sale.amount_paid:
                sale_cash_entries.append(CashEntry(
                    business=business,
                    entry_type=CashEntry.ENTRY_SALE_PAYMENT,
                    direction=CashEntry.DIRECTION_INFLOW,
                    amount=sale.amount_paid,
                    occurred_at=sold_at,
                    reference_type='sale',
                    reference_id=sale.id,
                    note=sale.note,
                ))

        SaleLine.objects.bulk_create(sale_lines, batch_size=500)
        for line, sold_at in zip(sale_lines, sale_dates):
            sale_movements.append(StockMovement(
                business=business,
                inventory_item=line.inventory_item,
                movement_type=StockMovement.MOVEMENT_SALE,
                quantity_change=-line.quantity,
                unit_cost=line.unit_cost,
                reference_type='sale_line',
                reference_id=line.id,
                note=f'Demo sale #{line.sale_id}',
            ))
            movement_dates.append(sold_at)
        StockMovement.objects.bulk_create(sale_movements, batch_size=500)
        for movement, created_at in zip(sale_movements, movement_dates):
            movement.created_at = created_at
        StockMovement.objects.bulk_update(sale_movements, ['created_at'], batch_size=500)
        CashEntry.objects.bulk_create(sale_cash_entries, batch_size=500)

        opening_date = local_datetime(first_day, 7)
        opening_movements = []
        opening_stock_value = Decimal('0.00')
        for item in inventory:
            opening_quantity = item.quantity + sold_quantities[item.id]
            opening_stock_value += item.unit_cost * opening_quantity
            opening_movements.append(StockMovement(
                business=business,
                inventory_item=item,
                movement_type=StockMovement.MOVEMENT_PURCHASE,
                quantity_change=opening_quantity,
                unit_cost=item.unit_cost,
                reference_type='demo_opening_stock',
                note='Opening stock for demo period',
            ))
        StockMovement.objects.bulk_create(opening_movements)
        for movement in opening_movements:
            movement.created_at = opening_date
        StockMovement.objects.bulk_update(opening_movements, ['created_at'])

        expense_specs = []
        for offset in range(90):
            day = first_day + timedelta(days=offset)
            if offset % 30 == 2:
                expense_specs.extend([
                    (day, 'Shop Rent', Expense.TYPE_OPERATING, Decimal('180000.00'), 'Monthly shop rent'),
                    (day, 'Staff Wages', Expense.TYPE_OPERATING, Decimal('150000.00'), 'Two shop attendants'),
                    (day, 'Electricity', Expense.TYPE_OPERATING, Decimal('45000.00'), 'Power and service charge'),
                    (day, 'Market Levy', Expense.TYPE_OPERATING, Decimal('12000.00'), 'Market association levy'),
                    (day, 'Mobile Data', Expense.TYPE_OPERATING, Decimal('9000.00'), 'Business internet subscription'),
                ])
            if offset % 7 == 1:
                expense_specs.append(
                    (day, 'Inventory Restock', Expense.TYPE_INVENTORY_PURCHASE,
                     Decimal(rng.randrange(140000, 280001, 5000)), 'Weekly supplier restock')
                )
            if offset % 7 == 3:
                expense_specs.append(
                    (day, 'Transport', Expense.TYPE_OPERATING, Decimal('18000.00'), 'Supplier collection and delivery')
                )
            if offset % 7 in (0, 4):
                expense_specs.append(
                    (day, 'Generator Fuel', Expense.TYPE_OPERATING, Decimal('12000.00'), 'Generator petrol')
                )
            if offset % 14 == 6:
                expense_specs.append(
                    (day, 'Packaging', Expense.TYPE_OPERATING, Decimal('15000.00'), 'Bags and wrapping materials')
                )

        expenses = [
            Expense(
                business=business,
                category=category,
                expense_type=expense_type,
                amount=amount,
                payment_status=Expense.PAYMENT_PAID,
                note=note,
                created_by=user,
            )
            for _, category, expense_type, amount, note in expense_specs
        ]
        Expense.objects.bulk_create(expenses)
        expense_dates = [
            local_datetime(day, 7 if expense_type == Expense.TYPE_INVENTORY_PURCHASE else 18)
            for day, _, expense_type, _, _ in expense_specs
        ]
        for expense, spent_at in zip(expenses, expense_dates):
            expense.spent_at = spent_at
        Expense.objects.bulk_update(expenses, ['spent_at'])

        expense_cash_entries = [
            CashEntry(
                business=business,
                entry_type=(
                    CashEntry.ENTRY_INVENTORY_PURCHASE
                    if expense.expense_type == Expense.TYPE_INVENTORY_PURCHASE
                    else CashEntry.ENTRY_EXPENSE_PAYMENT
                ),
                direction=CashEntry.DIRECTION_OUTFLOW,
                amount=expense.amount,
                occurred_at=spent_at,
                reference_type='expense',
                reference_id=expense.id,
                note=expense.note,
            )
            for expense, spent_at in zip(expenses, expense_dates)
        ]
        CashEntry.objects.bulk_create(expense_cash_entries)

        CashEntry.objects.bulk_create([
            CashEntry(
                business=business,
                entry_type=CashEntry.ENTRY_INVENTORY_PURCHASE,
                direction=CashEntry.DIRECTION_OUTFLOW,
                amount=opening_stock_value,
                occurred_at=opening_date,
                reference_type='demo_opening_stock',
                note='Opening grocery inventory',
            ),
            CashEntry(
                business=business,
                entry_type=CashEntry.ENTRY_OWNER_DEPOSIT,
                direction=CashEntry.DIRECTION_INFLOW,
                amount=Decimal('500000.00'),
                occurred_at=local_datetime(today - timedelta(days=70), 9),
                reference_type='demo_capital',
                note='Additional working capital',
            ),
            CashEntry(
                business=business,
                entry_type=CashEntry.ENTRY_OWNER_WITHDRAWAL,
                direction=CashEntry.DIRECTION_OUTFLOW,
                amount=Decimal('200000.00'),
                occurred_at=local_datetime(today - timedelta(days=12), 17),
                reference_type='demo_withdrawal',
                note='Owner profit withdrawal',
            ),
        ])

        sales_queryset = sales_for_business(business)
        expenses_queryset = expenses_for_business(business)
        lines_queryset = sale_lines_for_business(business)
        cash_queryset = cash_entries_for_business(business)
        forecast_for_business(
            business=business,
            sales=sales_queryset,
            expenses=expenses_queryset,
            sale_lines=lines_queryset,
            cash_entries=cash_queryset,
            lookback_days=90,
            horizon_days=30,
            persist=True,
            user=user,
        )
        estimate_tax_for_business(
            business=business,
            sales=sales_queryset,
            expenses=expenses_queryset,
            sale_lines=lines_queryset,
            persist=True,
        )

        self.stdout.write(self.style.SUCCESS('Demo account created successfully.'))
        self.stdout.write(f'Username: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(
            f'Data: {len(inventory)} inventory items, {len(sales)} sales, '
            f'{len(expenses)} expenses across {first_day} to {today}.'
        )
