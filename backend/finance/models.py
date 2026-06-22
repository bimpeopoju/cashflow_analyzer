from decimal import Decimal

from django.conf import settings
from django.db import models


class BusinessProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=120, default='MarketFlow Business')
    stall_name = models.CharField(max_length=120, blank=True)
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.business_name} ({self.user})'


class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_businesses',
    )
    name = models.CharField(max_length=120)
    stall_name = models.CharField(max_length=120, blank=True)
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class BusinessMembership(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'
    ROLE_VIEWER = 'viewer'
    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_VIEWER, 'Viewer'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_INVITED = 'invited'
    STATUS_DISABLED = 'disabled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INVITED, 'Invited'),
        (STATUS_DISABLED, 'Disabled'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'user'],
                name='unique_business_membership_user',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} in {self.business} ({self.role})'


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

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='sales')
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
        related_name='created_sales',
        null=True,
        blank=True,
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='voided_sales',
        null=True,
        blank=True,
    )
    void_reason = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-sold_at']

    def __str__(self) -> str:
        return f'{self.item_name} - {self.amount}'


class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='lines')
    inventory_item = models.ForeignKey(
        'InventoryItem',
        on_delete=models.SET_NULL,
        related_name='sale_lines',
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
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.item_name} x {self.quantity}'


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

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='expenses')
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
        related_name='created_expenses',
        null=True,
        blank=True,
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='voided_expenses',
        null=True,
        blank=True,
    )
    void_reason = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-spent_at']

    def __str__(self) -> str:
        return f'{self.category} - {self.amount}'


class InventoryItem(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_VOIDED = 'voided'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_VOIDED, 'Voided'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventory_items')
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
        related_name='created_inventory_items',
        null=True,
        blank=True,
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='voided_inventory_items',
        null=True,
        blank=True,
    )
    void_reason = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['name']

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

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='stock_movements')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity_change = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    reference_type = models.CharField(max_length=40, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self) -> str:
        return f'{self.inventory_item} {self.quantity_change}'


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

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='cash_entries')
    entry_type = models.CharField(max_length=40, choices=ENTRY_TYPE_CHOICES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    occurred_at = models.DateTimeField()
    reference_type = models.CharField(max_length=40, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at', '-id']

    def __str__(self) -> str:
        return f'{self.direction} {self.amount}'
