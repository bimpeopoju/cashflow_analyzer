from django.contrib import admin

from .models import BusinessProfile, Expense, InventoryItem, Sale


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'stall_name', 'initial_capital')
    search_fields = ('user__email', 'business_name', 'stall_name')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_name', 'amount', 'quantity', 'sold_at')
    list_filter = ('sold_at',)
    search_fields = ('user__email', 'item_name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'spent_at')
    list_filter = ('spent_at',)
    search_fields = ('user__email', 'category')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'quantity', 'unit', 'reorder_level', 'unit_cost')
    search_fields = ('user__email', 'name')
