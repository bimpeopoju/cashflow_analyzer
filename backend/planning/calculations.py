from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_CEILING

from django.db.models import Sum
from django.utils import timezone

from businesses.services import money
from expenses.models import Expense
from inventory.models import StockMovement


def decimal_text(value):
    return str((value or Decimal('0.00')).quantize(Decimal('0.01')))


def period_bounds(period_days):
    period_days = max(int(period_days or 30), 1)
    today = timezone.localdate()
    period_start_date = today - timedelta(days=period_days - 1)
    period_start = timezone.make_aware(datetime.combine(period_start_date, time.min))
    period_end = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min))
    return period_days, today, period_start_date, period_start, period_end


def burn_rate_for_business(*, inventory, stock_movements, period_days=30):
    period_days, today, period_start_date, period_start, period_end = period_bounds(period_days)

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


def break_even_for_business(*, sales, expenses, sale_lines, period_days=30):
    period_days, today, period_start_date, period_start, period_end = period_bounds(period_days)
    period_sales = sales.filter(sold_at__gte=period_start, sold_at__lt=period_end)
    period_expenses = expenses.filter(spent_at__gte=period_start, spent_at__lt=period_end)
    period_sale_lines = sale_lines.filter(sale__sold_at__gte=period_start, sale__sold_at__lt=period_end)

    actual_revenue = period_sale_lines.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
    if actual_revenue == 0:
        actual_revenue = period_sales.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    actual_units = period_sale_lines.aggregate(total=Sum('quantity'))['total'] or 0
    variable_costs = Decimal('0.00')
    for line in period_sale_lines:
        variable_costs += line.unit_cost * Decimal(line.quantity)

    fixed_costs = period_expenses.filter(expense_type=Expense.TYPE_OPERATING).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    if actual_units <= 0 or actual_revenue <= 0:
        return {
            'period': {
                'days': period_days,
                'startDate': period_start_date.isoformat(),
                'endDate': today.isoformat(),
            },
            'summary': {
                'status': 'no_data',
                'actualRevenue': money(actual_revenue),
                'actualUnitsSold': actual_units,
                'fixedCosts': money(fixed_costs),
                'variableCosts': money(variable_costs),
                'averageSellingPrice': money(Decimal('0.00')),
                'averageUnitVariableCost': money(Decimal('0.00')),
                'contributionMargin': money(Decimal('0.00')),
                'contributionMarginRatio': decimal_text(Decimal('0.00')),
                'breakEvenUnits': None,
                'breakEvenRevenue': None,
                'revenueGap': money(Decimal('0.00')),
                'unitsGap': 0,
            },
        }

    average_selling_price = actual_revenue / Decimal(actual_units)
    average_unit_variable_cost = variable_costs / Decimal(actual_units)
    contribution_margin = average_selling_price - average_unit_variable_cost

    if contribution_margin <= 0 or average_selling_price <= 0:
        status = 'unviable'
        contribution_margin_ratio = Decimal('0.00')
        break_even_units = None
        break_even_revenue = None
        revenue_gap = Decimal('0.00')
        units_gap = 0
    else:
        contribution_margin_ratio = contribution_margin / average_selling_price
        break_even_units = int((fixed_costs / contribution_margin).to_integral_value(rounding=ROUND_CEILING)) if fixed_costs > 0 else 0
        break_even_revenue = (fixed_costs / contribution_margin_ratio).quantize(Decimal('0.01')) if fixed_costs > 0 else Decimal('0.00')
        revenue_gap = max(break_even_revenue - actual_revenue, Decimal('0.00'))
        units_gap = max(break_even_units - actual_units, 0)
        status = 'above_break_even' if actual_revenue >= break_even_revenue else 'below_break_even'

    return {
        'period': {
            'days': period_days,
            'startDate': period_start_date.isoformat(),
            'endDate': today.isoformat(),
        },
        'summary': {
            'status': status,
            'actualRevenue': money(actual_revenue),
            'actualUnitsSold': actual_units,
            'fixedCosts': money(fixed_costs),
            'variableCosts': money(variable_costs),
            'averageSellingPrice': money(average_selling_price),
            'averageUnitVariableCost': money(average_unit_variable_cost),
            'contributionMargin': money(contribution_margin),
            'contributionMarginRatio': decimal_text(contribution_margin_ratio),
            'breakEvenUnits': break_even_units,
            'breakEvenRevenue': money(break_even_revenue) if break_even_revenue is not None else None,
            'revenueGap': money(revenue_gap),
            'unitsGap': units_gap,
        },
    }
