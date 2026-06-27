from decimal import Decimal

from django.conf import settings
from django.db import models


class ForecastRun(models.Model):
    METHOD_MOVING_AVERAGE_TREND = 'moving_average_trend'
    METHOD_CHOICES = [
        (METHOD_MOVING_AVERAGE_TREND, 'Moving average with trend adjustment'),
    ]

    CONFIDENCE_LOW = 'low'
    CONFIDENCE_MEDIUM = 'medium'
    CONFIDENCE_HIGH = 'high'
    CONFIDENCE_CHOICES = [
        (CONFIDENCE_LOW, 'Low'),
        (CONFIDENCE_MEDIUM, 'Medium'),
        (CONFIDENCE_HIGH, 'High'),
    ]

    GRANULARITY_DAILY = 'daily'
    GRANULARITY_CHOICES = [
        (GRANULARITY_DAILY, 'Daily'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    method = models.CharField(max_length=40, choices=METHOD_CHOICES, default=METHOD_MOVING_AVERAGE_TREND)
    lookback_days = models.PositiveIntegerField(default=30)
    horizon_days = models.PositiveIntegerField(default=14)
    period_granularity = models.CharField(max_length=20, choices=GRANULARITY_CHOICES, default=GRANULARITY_DAILY)
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_CHOICES, default=CONFIDENCE_LOW)
    warnings = models.JSONField(default=list, blank=True)
    assumptions = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Forecast {self.id} for business {self.business_id}'


class ForecastPeriod(models.Model):
    forecast_run = models.ForeignKey(ForecastRun, on_delete=models.CASCADE, related_name='periods')
    period_start = models.DateField()
    period_end = models.DateField()
    projected_sales = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    projected_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    projected_gross_profit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    projected_net_profit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    projected_cash_position = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    projected_inventory_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['period_start', 'id']

    def __str__(self):
        return f'{self.forecast_run_id}: {self.period_start} - {self.period_end}'
