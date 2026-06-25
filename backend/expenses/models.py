from decimal import Decimal

from django.conf import settings
from django.db import models


class Expense(models.Model):
    PAYMENT_PAID = 'paid'
    PAYMENT_UNPAID = 'unpaid'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_UNPAID, 'Unpaid'),
    ]
    TYPE_OPERATING = 'operating'
    TYPE_INVENTORY_PURCHASE = 'inventory_purchase'
    TYPE_TAX = 'tax'
    TYPE_CAPITAL = 'capital'
    TYPE_PERSONAL_WITHDRAWAL = 'personal_withdrawal'
    TYPE_OTHER = 'other'
    EXPENSE_TYPE_CHOICES = [
        (TYPE_OPERATING, 'Operating'),
        (TYPE_INVENTORY_PURCHASE, 'Inventory purchase'),
        (TYPE_TAX, 'Tax'),
        (TYPE_CAPITAL, 'Capital'),
        (TYPE_PERSONAL_WITHDRAWAL, 'Personal withdrawal'),
        (TYPE_OTHER, 'Other'),
    ]
    STATUS_APPROVED = 'approved'
    STATUS_VOIDED = 'voided'
    STATUS_CHOICES = [
        (STATUS_APPROVED, 'Approved'),
        (STATUS_VOIDED, 'Voided'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    category = models.CharField(max_length=120)
    expense_type = models.CharField(max_length=40, choices=EXPENSE_TYPE_CHOICES, default=TYPE_OPERATING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PAID)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    note = models.CharField(max_length=240, blank=True)
    spent_at = models.DateTimeField(auto_now_add=True)
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
        db_table = 'finance_expense'
        ordering = ['-spent_at']
        managed = False

    def __str__(self) -> str:
        return f'{self.category} - {self.amount}'
