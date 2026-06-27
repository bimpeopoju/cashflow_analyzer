from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_CEILING

from django.db.models import Sum
from django.utils import timezone

from businesses.services import money
from inventory.models import StockMovement


def decimal_text(value):
    return str((value or Decimal('0.00')).quantize(Decimal('0.01')))


def burn_rate_for_business(*, inventory, stock_movements, period_days=30):
    period_days = max(int(period_days or 30), 1)
    today = timezone.localdate()
    period_start_date = today - timedelta(days=period_days - 1)
    period_start = timezone.make_aware(datetime.combine(period_start_date, time.min))
    period_end = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min))

    rows = []
    active_burn_items = 0
    at_risk_items = 0
    total_consumed_value = Decimal('0.00')

    for item in inventory:
        item_movements = stock_movements.filter(inventory_item=item, created_at__gte=period_start, created_at__lt=period_end)
        sold_quantity = abs(item_movements.filter(
            movement_type=StockMovement.MOVEMENT_SALE,
            quantity_change__lt=0,
        ).aggregate(total=Sum('quantity_change'))['total'] or 0)
        returned_quantity = item_movements.filter(
            movement_type=StockMovement.MOVEMENT_RETURN,
            quantity_change__gt=0,
        ).aggregate(total=Sum('quantity_change'))['total'] or 0
        net_consumed = max(sold_quantity - returned_quantity, 0)
        average_daily = (Decimal(net_consumed) / Decimal(period_days)).quantize(Decimal('0.01'))
        consumed_value = (Decimal(net_consumed) * item.unit_cost).quantize(Decimal('0.01'))
        total_consumed_value += consumed_value

        if average_daily > 0:
            active_burn_items += 1
            days_until_stockout_decimal = Decimal(item.quantity) / average_daily
            days_until_stockout = int(days_until_stockout_decimal.to_integral_value(rounding=ROUND_CEILING))
            projected_stockout_date = (today + timedelta(days=days_until_stockout)).isoformat()
        else:
            days_until_stockout = None
            projected_stockout_date = None

        if item.quantity <= 0:
            status = 'out'
            at_risk_items += 1
        elif average_daily == 0:
            status = 'no_data'
        elif item.quantity <= item.reorder_level or (days_until_stockout is not None and days_until_stockout <= 7):
            status = 'at_risk'
            at_risk_items += 1
        else:
            status = 'stable'

        rows.append({
            'itemId': item.id,
            'name': item.name,
            'unit': item.unit,
            'currentQuantity': item.quantity,
            'reorderLevel': item.reorder_level,
            'periodDays': period_days,
            'consumedQuantity': net_consumed,
            'averageDailyConsumption': decimal_text(average_daily),
            'daysUntilStockout': days_until_stockout,
            'projectedStockoutDate': projected_stockout_date,
            'consumedValue': money(consumed_value),
            'status': status,
        })

    rows.sort(key=lambda row: (
        row['daysUntilStockout'] is None,
        row['daysUntilStockout'] if row['daysUntilStockout'] is not None else 999999,
        row['name'].lower(),
    ))

    return {
        'period': {
            'days': period_days,
            'startDate': period_start_date.isoformat(),
            'endDate': today.isoformat(),
        },
        'summary': {
            'trackedItems': len(rows),
            'activeBurnItems': active_burn_items,
            'atRiskItems': at_risk_items,
            'totalConsumedValue': money(total_consumed_value),
        },
        'items': rows,
    }
