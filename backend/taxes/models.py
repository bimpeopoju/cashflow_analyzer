from decimal import Decimal

from django.db import models


class TaxRule(models.Model):
    TYPE_VAT = 'vat'
    TYPE_CIT = 'cit'
    TYPE_CHOICES = [
        (TYPE_VAT, 'Value Added Tax'),
        (TYPE_CIT, 'Company Income Tax'),
    ]

    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    jurisdiction = models.CharField(max_length=80, default='Nigeria')
    tax_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    rate = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal('0.0000'))
    threshold_min = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    threshold_max = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    configuration = models.JSONField(default=dict, blank=True)
    source_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tax_type', 'threshold_min', '-effective_from']

    def __str__(self):
        return f'{self.code} ({self.rate})'


class TaxEstimate(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    period_start = models.DateField()
    period_end = models.DateField()
    rule_snapshot = models.JSONField(default=dict)
    assumptions = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Tax estimate for {self.business_id}: {self.period_start} - {self.period_end}'
