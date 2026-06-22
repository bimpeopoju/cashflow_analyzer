from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from .serializers import inventory_payload
from .services import money


def dashboard_for_business(*, business, sales, expenses, inventory):
    today = timezone.localdate()
    start = timezone.make_aware(datetime.combine(today, time.min))
    week_start = start - timedelta(days=6)

    sales_today = sales.filter(sold_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expenses_today = expenses.filter(spent_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_sales = sales.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    net_profit = total_sales - total_expenses

    recent = [
        {
            'id': f'sale-{sale.id}',
            'kind': 'sale',
            'label': sale.item_name,
            'amount': money(sale.amount),
            'createdAt': sale.sold_at.isoformat(),
        }
        for sale in sales[:5]
    ] + [
        {
            'id': f'expense-{expense.id}',
            'kind': 'expense',
            'label': expense.category,
            'amount': money(expense.amount),
            'createdAt': expense.spent_at.isoformat(),
        }
        for expense in expenses[:5]
    ]
    recent.sort(key=lambda item: item['createdAt'], reverse=True)

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

    low_stock = [
        inventory_payload(item)
        for item in inventory
        if item.quantity <= item.reorder_level
    ][:5]

    top_sale = sales.filter(sold_at__gte=week_start).values('item_name').annotate(total=Sum('amount')).order_by('-total').first()

    return {
        'summary': {
            'salesToday': money(sales_today),
            'expensesToday': money(expenses_today),
            'netProfit': money(net_profit),
            'transactionsToday': sales.filter(sold_at__gte=start).count() + expenses.filter(spent_at__gte=start).count(),
            'initialCapital': money(business.initial_capital),
            'currentCapital': money(business.initial_capital + net_profit),
            'inventoryValue': money(sum((item.unit_cost * item.quantity for item in inventory), Decimal('0.00'))),
        },
        'recentActivity': recent[:6],
        'lowStock': low_stock,
        'topSelling': {
            'name': top_sale['item_name'] if top_sale else 'No sales yet',
            'amount': money(top_sale['total']) if top_sale else '0.00',
        },
        'weeklyPerformance': weekly,
    }
