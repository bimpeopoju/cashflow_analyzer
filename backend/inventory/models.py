from decimal import Decimal

from django.conf import settings
from django.db import models


class InventoryItem(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_VOIDED = 'voided'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_VOIDED, 'Voided'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=40, default='pcs')
    reorder_level = models.PositiveIntegerField(default=5)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
        db_table = 'finance_inventoryitem'
        ordering = ['name']
        managed = False

    def __str__(self) -> str:
        return self.name


class StockMovement(models.Model):
    MOVEMENT_PURCHASE = 'purchase'
    MOVEMENT_SALE = 'sale'
    MOVEMENT_ADJUSTMENT = 'adjustment'
    MOVEMENT_LOSS = 'loss'
    MOVEMENT_RETURN = 'return'
    MOVEMENT_CHOICES = [
        (MOVEMENT_PURCHASE, 'Purchase'),
        (MOVEMENT_SALE, 'Sale'),
        (MOVEMENT_ADJUSTMENT, 'Adjustment'),
        (MOVEMENT_LOSS, 'Loss'),
        (MOVEMENT_RETURN, 'Return'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='+')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity_change = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    reference_type = models.CharField(max_length=40, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_stockmovement'
        ordering = ['-created_at', '-id']
        managed = False

    def __str__(self) -> str:
        return f'{self.inventory_item} {self.quantity_change}'
