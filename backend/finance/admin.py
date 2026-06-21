from django.contrib import admin

from .models import Business, BusinessMembership, BusinessProfile, Expense, InventoryItem, Sale


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
    list_display = ('business', 'item_name', 'amount', 'quantity', 'sold_at')
    list_filter = ('sold_at',)
    search_fields = ('business__name', 'item_name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('business', 'category', 'amount', 'spent_at')
    list_filter = ('spent_at',)
    search_fields = ('business__name', 'category')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('business', 'name', 'quantity', 'unit', 'reorder_level', 'unit_cost')
    search_fields = ('business__name', 'name')
