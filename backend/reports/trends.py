from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from businesses.services import money


def growth_rate(current, previous):
    if previous == 0:
        return None
    return ((current - previous) / abs(previous) * Decimal('100')).quantize(Decimal('0.01'))


def trend_direction(current, previous):
    if previous == 0 and current > 0:
        return 'new'
    if current > previous:
        return 'up'
    if current < previous:
        return 'down'
    return 'flat'


def metric_payload(current, previous):
    rate = growth_rate(current, previous)
    return {
        'current': money(current),
        'previous': money(previous),
        'change': money(current - previous),
        'growthRate': str(rate) if rate is not None else None,
        'direction': trend_direction(current, previous),
    }


def weekly_trends_for_business(*, sales, expenses):
    today = timezone.localdate()
    current_start_date = today - timedelta(days=6)
    previous_start_date = current_start_date - timedelta(days=7)
    current_start = timezone.make_aware(datetime.combine(current_start_date, time.min))
    previous_start = timezone.make_aware(datetime.combine(previous_start_date, time.min))

    current_sales = sales.filter(sold_at__gte=current_start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    previous_sales = sales.filter(sold_at__gte=previous_start, sold_at__lt=current_start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    current_expenses = expenses.filter(spent_at__gte=current_start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    previous_expenses = expenses.filter(spent_at__gte=previous_start, spent_at__lt=current_start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    current_profit = current_sales - current_expenses
    previous_profit = previous_sales - previous_expenses

    daily = []
    cumulative_sales = Decimal('0.00')
    cumulative_profit = Decimal('0.00')
    best_day = None

    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        day_start = timezone.make_aware(datetime.combine(day, time.min))
        day_end = day_start + timedelta(days=1)
        day_sales = sales.filter(sold_at__gte=day_start, sold_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_expenses = expenses.filter(spent_at__gte=day_start, spent_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_profit = day_sales - day_expenses
        cumulative_sales += day_sales
        cumulative_profit += day_profit
        row = {
            'date': day.isoformat(),
            'day': day.strftime('%a'),
            'sales': money(day_sales),
            'expenses': money(day_expenses),
            'netProfit': money(day_profit),
            'cumulativeSales': money(cumulative_sales),
            'cumulativeProfit': money(cumulative_profit),
        }
        daily.append(row)
        if best_day is None or day_sales > Decimal(best_day['sales']):
            best_day = row

    return {
        'period': {
            'currentStartDate': current_start_date.isoformat(),
            'currentEndDate': today.isoformat(),
            'previousStartDate': previous_start_date.isoformat(),
            'previousEndDate': (current_start_date - timedelta(days=1)).isoformat(),
        },
        'summary': {
            'sales': metric_payload(current_sales, previous_sales),
            'expenses': metric_payload(current_expenses, previous_expenses),
            'netProfit': metric_payload(current_profit, previous_profit),
            'bestSalesDay': best_day,
        },
        'daily': daily,
    }
