import decimal

import django.db.models.deletion
from django.db import migrations, models


def backfill_sale_lines(apps, schema_editor):
    Sale = apps.get_model('finance', 'Sale')
    SaleLine = apps.get_model('finance', 'SaleLine')

    for sale in Sale.objects.all().iterator():
        quantity = sale.quantity or 1
        unit_price = (sale.amount / quantity).quantize(decimal.Decimal('0.01'))
        SaleLine.objects.create(
            sale_id=sale.id,
            inventory_item_id=None,
            item_name=sale.item_name,
            quantity=quantity,
            unit_price=unit_price,
            unit_cost=decimal.Decimal('0.00'),
            discount_amount=decimal.Decimal('0.00'),
            line_total=sale.amount,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_business_ownership'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=120)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('inventory_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_lines', to='finance.inventoryitem')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='finance.sale')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(choices=[('purchase', 'Purchase'), ('sale', 'Sale'), ('adjustment', 'Adjustment'), ('loss', 'Loss'), ('return', 'Return')], max_length=20)),
                ('quantity_change', models.IntegerField()),
                ('unit_cost', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('reference_type', models.CharField(blank=True, max_length=40)),
                ('reference_id', models.PositiveIntegerField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=240)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='finance.business')),
                ('inventory_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='finance.inventoryitem')),
            ],
            options={
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.RunPython(backfill_sale_lines, migrations.RunPython.noop),
    ]
