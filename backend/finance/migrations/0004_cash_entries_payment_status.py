import decimal

import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def backfill_cash_entries(apps, schema_editor):
    Sale = apps.get_model('finance', 'Sale')
    Expense = apps.get_model('finance', 'Expense')
    InventoryItem = apps.get_model('finance', 'InventoryItem')
    CashEntry = apps.get_model('finance', 'CashEntry')

    for sale in Sale.objects.all().iterator():
        sale.amount_paid = sale.amount
        sale.payment_status = 'paid'
        sale.save(update_fields=['amount_paid', 'payment_status'])
        if sale.amount > 0:
            CashEntry.objects.create(
                business_id=sale.business_id,
                entry_type='sale_payment',
                direction='inflow',
                amount=sale.amount,
                occurred_at=sale.sold_at,
                reference_type='sale',
                reference_id=sale.id,
                note='Backfilled from existing sale.',
            )

    for expense in Expense.objects.all().iterator():
        expense.payment_status = 'paid'
        expense.save(update_fields=['payment_status'])
        if expense.amount > 0:
            CashEntry.objects.create(
                business_id=expense.business_id,
                entry_type='expense_payment',
                direction='outflow',
                amount=expense.amount,
                occurred_at=expense.spent_at,
                reference_type='expense',
                reference_id=expense.id,
                note='Backfilled from existing expense.',
            )

    now = timezone.now()
    for item in InventoryItem.objects.all().iterator():
        stock_value = (item.unit_cost * item.quantity).quantize(decimal.Decimal('0.01'))
        if stock_value > 0:
            CashEntry.objects.create(
                business_id=item.business_id,
                entry_type='inventory_purchase',
                direction='outflow',
                amount=stock_value,
                occurred_at=item.created_at or now,
                reference_type='inventory_item',
                reference_id=item.id,
                note='Backfilled from existing inventory value.',
            )


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_sale_lines_stock_movements'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='paid', max_length=20),
        ),
        migrations.AddField(
            model_name='sale',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12),
        ),
        migrations.AddField(
            model_name='sale',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('partial', 'Partial'), ('unpaid', 'Unpaid')], default='paid', max_length=20),
        ),
        migrations.CreateModel(
            name='CashEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_type', models.CharField(choices=[('sale_payment', 'Sale payment'), ('expense_payment', 'Expense payment'), ('inventory_purchase', 'Inventory purchase'), ('owner_deposit', 'Owner deposit'), ('owner_withdrawal', 'Owner withdrawal'), ('tax_payment', 'Tax payment'), ('other', 'Other')], max_length=40)),
                ('direction', models.CharField(choices=[('inflow', 'Inflow'), ('outflow', 'Outflow')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('occurred_at', models.DateTimeField()),
                ('reference_type', models.CharField(blank=True, max_length=40)),
                ('reference_id', models.PositiveIntegerField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=240)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_entries', to='finance.business')),
            ],
            options={
                'ordering': ['-occurred_at', '-id'],
            },
        ),
        migrations.RunPython(backfill_cash_entries, migrations.RunPython.noop),
    ]
