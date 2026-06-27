from datetime import date
from decimal import Decimal

from django.db import migrations


def seed_rules(apps, schema_editor):
    TaxRule = apps.get_model('taxes', 'TaxRule')
    rules = [
        {
            'code': 'NG_VAT_STANDARD_2020',
            'name': 'Nigeria standard VAT',
            'tax_type': 'vat',
            'rate': Decimal('0.0750'),
            'effective_from': date(2020, 2, 1),
            'source_url': 'https://taxsummaries.pwc.com/nigeria/corporate/other-taxes',
            'notes': 'Standard VAT estimate rate. Zero-rated, exempt, reverse-charge, and input VAT rules require transaction-level classification.',
        },
        {
            'code': 'NG_CIT_SMALL_2025',
            'name': 'Nigeria CIT small company',
            'tax_type': 'cit',
            'rate': Decimal('0.0000'),
            'threshold_min': Decimal('0.00'),
            'threshold_max': Decimal('100000000.00'),
            'effective_from': date(2025, 1, 1),
            'source_url': 'https://taxsummaries.pwc.com/nigeria/corporate/taxes-on-corporate-income',
            'notes': 'Small company turnover band estimate. Fixed-asset and entity-specific requirements are not yet captured.',
        },
        {
            'code': 'NG_CIT_STANDARD_2025',
            'name': 'Nigeria CIT standard company',
            'tax_type': 'cit',
            'rate': Decimal('0.3000'),
            'threshold_min': Decimal('100000000.01'),
            'effective_from': date(2025, 1, 1),
            'source_url': 'https://taxsummaries.pwc.com/nigeria/corporate/taxes-on-corporate-income',
            'notes': 'Standard company income tax estimate by turnover band.',
        },
    ]
    for rule in rules:
        TaxRule.objects.update_or_create(code=rule['code'], defaults=rule)


def remove_rules(apps, schema_editor):
    TaxRule = apps.get_model('taxes', 'TaxRule')
    TaxRule.objects.filter(code__in=[
        'NG_VAT_STANDARD_2020',
        'NG_CIT_SMALL_2025',
        'NG_CIT_STANDARD_2025',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('taxes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_rules, remove_rules),
    ]
