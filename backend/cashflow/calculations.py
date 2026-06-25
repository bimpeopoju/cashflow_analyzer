from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from businesses.services import money
from cashflow.models import CashEntry
from expenses.models import Expense
from sales.models import Sale, SaleLine


def capital_summary_for_business(*, business, sales=None, expenses=None, sale_lines=None, cash_entries=None, inventory=None):
    sales = sales if sales is not None else Sale.objects.filter(business=business, status=Sale.STATUS_COMPLETED)
    expenses = expenses if expenses is not None else Expense.objects.filter(business=business, status=Expense.STATUS_APPROVED)
    sale_lines = sale_lines if sale_lines is not None else SaleLine.objects.filter(
        sale__business=business,
        sale__status=Sale.STATUS_COMPLETED,
    )
    cash_entries = cash_entries if cash_entries is not None else CashEntry.objects.filter(business=business)
    inventory = inventory if inventory is not None else []

    today = timezone.localdate()
    start = timezone.make_aware(datetime.combine(today, time.min))
    week_start = start - timedelta(days=6)

    sales_today = sales.filter(sold_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expenses_today = expenses.filter(spent_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_sales = sales.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    cost_of_goods_sold = (
        sale_lines.annotate(line_cost=F('unit_cost') * F('quantity'))
        .aggregate(total=Sum('line_cost'))['total']
        or Decimal('0.00')
    )

    owner_contributions = (
        cash_entries.filter(entry_type=CashEntry.ENTRY_OWNER_DEPOSIT, direction=CashEntry.DIRECTION_INFLOW)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    owner_withdrawals = (
        cash_entries.filter(entry_type=CashEntry.ENTRY_OWNER_WITHDRAWAL, direction=CashEntry.DIRECTION_OUTFLOW)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    cash_inflow = cash_entries.filter(direction=CashEntry.DIRECTION_INFLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    cash_outflow = cash_entries.filter(direction=CashEntry.DIRECTION_OUTFLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    cash_position = business.initial_capital + cash_inflow - cash_outflow

    gross_profit = total_sales - cost_of_goods_sold
    net_profit = gross_profit - total_expenses
    protected_capital_floor = business.initial_capital + owner_contributions
    equity_position = protected_capital_floor + net_profit - owner_withdrawals
    capital_gap = max(protected_capital_floor - equity_position, Decimal('0.00'))
    capital_eroded = capital_gap > 0
    available_profit_for_withdrawal = max(net_profit - owner_withdrawals, Decimal('0.00'))
    retained_profit = net_profit - owner_withdrawals
    outstanding_sales = total_sales - (
        sales.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
    )

    weekly = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        day_start = timezone.make_aware(datetime.combine(day, time.min))
        day_end = day_start + timedelta(days=1)
        day_sales = sales.filter(sold_at__gte=day_start, sold_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_expenses = expenses.filter(spent_at__gte=day_start, spent_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        weekly.append({
            'day': day.strftime('%a'),
            'sales': money(day_sales),
            'expenses': money(day_expenses),
        })

    top_sale = sales.filter(sold_at__gte=week_start).values('item_name').annotate(total=Sum('amount')).order_by('-total').first()

    inventory_value = sum((item.unit_cost * item.quantity for item in inventory), Decimal('0.00'))

    return {
        'summary': {
            'salesToday': money(sales_today),
            'expensesToday': money(expenses_today),
            'costOfGoodsSold': money(cost_of_goods_sold),
            'grossProfit': money(gross_profit),
            'netProfit': money(net_profit),
            'cashInflow': money(cash_inflow),
            'cashOutflow': money(cash_outflow),
            'cashPosition': money(cash_position),
            'outstandingSales': money(outstanding_sales),
            'transactionsToday': sales.filter(sold_at__gte=start).count() + expenses.filter(spent_at__gte=start).count(),
            'initialCapital': money(business.initial_capital),
            'capitalContributions': money(owner_contributions),
            'capitalWithdrawals': money(owner_withdrawals),
            'protectedCapitalFloor': money(protected_capital_floor),
            'retainedProfit': money(retained_profit),
            'currentCapital': money(equity_position),
            'capitalGap': money(capital_gap),
            'capitalEroded': capital_eroded,
            'availableProfit': money(available_profit_for_withdrawal),
            'inventoryValue': money(inventory_value),
        },
        'weeklyPerformance': weekly,
        'topSelling': {
            'name': top_sale['item_name'] if top_sale else 'No sales yet',
            'amount': money(top_sale['total']) if top_sale else '0.00',
        },
    }
