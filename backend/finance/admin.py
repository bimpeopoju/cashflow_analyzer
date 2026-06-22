from django.contrib import admin

from .models import (
    Business,
    BusinessMembership,
    BusinessProfile,
    CashEntry,
    Expense,
    InventoryItem,
    Sale,
    SaleLine,
    StockMovement,
)


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'stall_name', 'initial_capital')
    search_fields = ('user__email', 'business_name', 'stall_name')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'stall_name', 'initial_capital')
    search_fields = ('name', 'stall_name', 'owner__email')


@admin.register(BusinessMembership)
class BusinessMembershipAdmin(admin.ModelAdmin):
    list_display = ('business', 'user', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('business__name', 'user__email')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('business', 'item_name', 'amount', 'amount_paid', 'payment_status', 'status', 'quantity', 'sold_at')
    list_filter = ('payment_status', 'status', 'sold_at')
    search_fields = ('business__name', 'item_name')


@admin.register(SaleLine)
class SaleLineAdmin(admin.ModelAdmin):
    list_display = ('sale', 'item_name', 'quantity', 'unit_price', 'unit_cost', 'line_total')
    search_fields = ('sale__business__name', 'item_name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('business', 'category', 'expense_type', 'amount', 'payment_status', 'status', 'spent_at')
    list_filter = ('expense_type', 'payment_status', 'status', 'spent_at')
    search_fields = ('business__name', 'category')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('business', 'name', 'quantity', 'unit', 'reorder_level', 'unit_cost', 'status')
    list_filter = ('status',)
    search_fields = ('business__name', 'name')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('business', 'inventory_item', 'movement_type', 'quantity_change', 'unit_cost', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('business__name', 'inventory_item__name', 'reference_type')


@admin.register(CashEntry)
class CashEntryAdmin(admin.ModelAdmin):
    list_display = ('business', 'entry_type', 'direction', 'amount', 'occurred_at', 'reference_type', 'reference_id')
    list_filter = ('entry_type', 'direction', 'occurred_at')
    search_fields = ('business__name', 'reference_type', 'note')
