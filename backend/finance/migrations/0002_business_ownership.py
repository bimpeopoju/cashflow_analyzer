import decimal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def forwards(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    BusinessProfile = apps.get_model('finance', 'BusinessProfile')
    Business = apps.get_model('finance', 'Business')
    BusinessMembership = apps.get_model('finance', 'BusinessMembership')
    Sale = apps.get_model('finance', 'Sale')
    Expense = apps.get_model('finance', 'Expense')
    InventoryItem = apps.get_model('finance', 'InventoryItem')

    business_by_user_id = {}

    for profile in BusinessProfile.objects.select_related('user').all():
        business = Business.objects.create(
            owner_id=profile.user_id,
            name=profile.business_name,
            stall_name=profile.stall_name,
            initial_capital=profile.initial_capital,
        )
        BusinessMembership.objects.create(
            business=business,
            user_id=profile.user_id,
            role='owner',
            status='active',
        )
        business_by_user_id[profile.user_id] = business.id

    user_ids = set(User.objects.values_list('id', flat=True))
    for user_id in user_ids:
        if user_id in business_by_user_id:
            continue
        user = User.objects.get(id=user_id)
        label = user.first_name or 'MarketFlow'
        business = Business.objects.create(
            owner_id=user_id,
            name=f'{label} Business',
            stall_name='Market stall',
            initial_capital=decimal.Decimal('0.00'),
        )
        BusinessMembership.objects.create(
            business=business,
            user_id=user_id,
            role='owner',
            status='active',
        )
        business_by_user_id[user_id] = business.id

    for user_id, business_id in business_by_user_id.items():
        Sale.objects.filter(user_id=user_id).update(business_id=business_id)
        Expense.objects.filter(user_id=user_id).update(business_id=business_id)
        InventoryItem.objects.filter(user_id=user_id).update(business_id=business_id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('stall_name', models.CharField(blank=True, max_length=120)),
                ('initial_capital', models.DecimalField(decimal_places=2, default=decimal.Decimal('0.00'), max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owned_businesses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BusinessMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('staff', 'Staff'), ('viewer', 'Viewer')], default='staff', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('invited', 'Invited'), ('disabled', 'Disabled')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='finance.business')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_memberships', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='expense',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='finance.business'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='finance.business'),
        ),
        migrations.AddField(
            model_name='sale',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='finance.business'),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='expense',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='finance.business'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='finance.business'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='finance.business'),
        ),
        migrations.RemoveField(
            model_name='expense',
            name='user',
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='user',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='user',
        ),
        migrations.AddConstraint(
            model_name='businessmembership',
            constraint=models.UniqueConstraint(fields=('business', 'user'), name='unique_business_membership_user'),
        ),
    ]
