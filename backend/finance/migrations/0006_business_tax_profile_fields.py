from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0005_audit_status_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='accounting_year_end_day',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='business',
            name='accounting_year_end_month',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='business',
            name='entity_type',
            field=models.CharField(blank=True, choices=[('company', 'Company'), ('sole_proprietor', 'Sole proprietor'), ('partnership', 'Partnership')], max_length=24),
        ),
        migrations.AddField(
            model_name='business',
            name='tin',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='business',
            name='vat_registered',
            field=models.BooleanField(default=False),
        ),
    ]
