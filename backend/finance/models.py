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
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='sales')
    item_name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    note = models.CharField(max_length=240, blank=True)
    sold_at = models.DateTimeField(auto_now_add=True)

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
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=240, blank=True)
    spent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-spent_at']

    def __str__(self) -> str:
        return f'{self.category} - {self.amount}'


class InventoryItem(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventory_items')
    name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=40, default='pcs')
    reorder_level = models.PositiveIntegerField(default=5)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
