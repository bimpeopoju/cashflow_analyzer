import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0004_cash_entries_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_expenses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expense',
            name='expense_type',
            field=models.CharField(choices=[('operating', 'Operating'), ('inventory_purchase', 'Inventory purchase'), ('tax', 'Tax'), ('capital', 'Capital'), ('personal_withdrawal', 'Personal withdrawal'), ('other', 'Other')], default='operating', max_length=40),
        ),
        migrations.AddField(
            model_name='expense',
            name='status',
            field=models.CharField(choices=[('approved', 'Approved'), ('voided', 'Voided')], default='approved', max_length=20),
        ),
        migrations.AddField(
            model_name='expense',
            name='void_reason',
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name='expense',
            name='voided_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='voided_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voided_expenses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_inventory_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('voided', 'Voided')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='void_reason',
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='voided_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='voided_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voided_inventory_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sale',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_sales', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sale',
            name='status',
            field=models.CharField(choices=[('completed', 'Completed'), ('voided', 'Voided'), ('refunded', 'Refunded')], default='completed', max_length=20),
        ),
        migrations.AddField(
            model_name='sale',
            name='void_reason',
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name='sale',
            name='voided_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sale',
            name='voided_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voided_sales', to=settings.AUTH_USER_MODEL),
        ),
    ]
