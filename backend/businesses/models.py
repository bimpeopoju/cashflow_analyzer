from decimal import Decimal

from django.conf import settings
from django.db import models


class BusinessProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    business_name = models.CharField(max_length=120, default='MarketFlow Business')
    stall_name = models.CharField(max_length=120, blank=True)
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_businessprofile'
        managed = False

    def __str__(self) -> str:
        return f'{self.business_name} ({self.user})'


class Business(models.Model):
    ENTITY_COMPANY = 'company'
    ENTITY_SOLE_PROPRIETOR = 'sole_proprietor'
    ENTITY_PARTNERSHIP = 'partnership'
    ENTITY_CHOICES = [
        (ENTITY_COMPANY, 'Company'),
        (ENTITY_SOLE_PROPRIETOR, 'Sole proprietor'),
        (ENTITY_PARTNERSHIP, 'Partnership'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
    )
    name = models.CharField(max_length=120)
    stall_name = models.CharField(max_length=120, blank=True)
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tin = models.CharField(max_length=32, blank=True)
    entity_type = models.CharField(max_length=24, choices=ENTITY_CHOICES, blank=True)
    vat_registered = models.BooleanField(default=False)
    accounting_year_end_month = models.PositiveSmallIntegerField(null=True, blank=True)
    accounting_year_end_day = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_business'
        ordering = ['name']
        managed = False

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
        related_name='+',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STAFF)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_businessmembership'
        constraints = []
        managed = False

    def __str__(self) -> str:
        return f'{self.user} in {self.business} ({self.role})'
