from decimal import Decimal

from django.conf import settings
from django.db import models


class Sale(models.Model):
    PAYMENT_PAID = 'paid'
    PAYMENT_PARTIAL = 'partial'
    PAYMENT_UNPAID = 'unpaid'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_PARTIAL, 'Partial'),
        (PAYMENT_UNPAID, 'Unpaid'),
    ]
    STATUS_COMPLETED = 'completed'
    STATUS_VOIDED = 'voided'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_VOIDED, 'Voided'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    item_name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PAID)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMPLETED)
    quantity = models.PositiveIntegerField(default=1)
    note = models.CharField(max_length=240, blank=True)
    sold_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    void_reason = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = 'finance_sale'
        ordering = ['-sold_at']
        managed = False

    def __str__(self) -> str:
        return f'{self.item_name} - {self.amount}'


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='+')
    inventory_item = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    item_name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_saleline'
        ordering = ['id']
        managed = False

    def __str__(self) -> str:
        return f'{self.item_name} x {self.quantity}'
