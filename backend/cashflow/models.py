from django.db import models


class CashEntry(models.Model):
    ENTRY_SALE_PAYMENT = 'sale_payment'
    ENTRY_EXPENSE_PAYMENT = 'expense_payment'
    ENTRY_INVENTORY_PURCHASE = 'inventory_purchase'
    ENTRY_OWNER_DEPOSIT = 'owner_deposit'
    ENTRY_OWNER_WITHDRAWAL = 'owner_withdrawal'
    ENTRY_TAX_PAYMENT = 'tax_payment'
    ENTRY_OTHER = 'other'
    ENTRY_TYPE_CHOICES = [
        (ENTRY_SALE_PAYMENT, 'Sale payment'),
        (ENTRY_EXPENSE_PAYMENT, 'Expense payment'),
        (ENTRY_INVENTORY_PURCHASE, 'Inventory purchase'),
        (ENTRY_OWNER_DEPOSIT, 'Owner deposit'),
        (ENTRY_OWNER_WITHDRAWAL, 'Owner withdrawal'),
        (ENTRY_TAX_PAYMENT, 'Tax payment'),
        (ENTRY_OTHER, 'Other'),
    ]

    DIRECTION_INFLOW = 'inflow'
    DIRECTION_OUTFLOW = 'outflow'
    DIRECTION_CHOICES = [
        (DIRECTION_INFLOW, 'Inflow'),
        (DIRECTION_OUTFLOW, 'Outflow'),
    ]

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='+')
    entry_type = models.CharField(max_length=40, choices=ENTRY_TYPE_CHOICES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    occurred_at = models.DateTimeField()
    reference_type = models.CharField(max_length=40, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_cashentry'
        ordering = ['-occurred_at', '-id']
        managed = False

    def __str__(self) -> str:
        return f'{self.direction} {self.amount}'
