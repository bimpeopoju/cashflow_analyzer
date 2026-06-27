from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from businesses.services import money
from cashflow.models import CashEntry
from expenses.models import Expense
from forecasting.models import ForecastPeriod, ForecastRun


class ForecastDataUnavailable(ValueError):
    pass


def clamp_days(value, *, default, minimum, maximum):
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, minimum), maximum)


def decimal_average(values):
    if not values:
        return Decimal('0.00')
    return sum(values, Decimal('0.00')) / Decimal(len(values))


def forecast_daily_value(values, trend_weight=Decimal('0.50')):
    baseline = decimal_average(values)
    if not values:
        return Decimal('0.00')
    recent_window = max(len(values) // 3, 1)
    recent_average = decimal_average(values[-recent_window:])
    projected = baseline + (trend_weight * (recent_average - baseline))
    return max(projected, Decimal('0.00'))


def confidence_for_history(*, active_days, lookback_days, warnings):
    if active_days < 7 or warnings:
        return ForecastRun.CONFIDENCE_LOW
    if active_days < max(lookback_days // 2, 7):
        return ForecastRun.CONFIDENCE_MEDIUM
    return ForecastRun.CONFIDENCE_HIGH


def period_payload(period):
    return {
        'periodStart': period.period_start.isoformat(),
        'periodEnd': period.period_end.isoformat(),
        'projectedSales': money(period.projected_sales),
        'projectedExpenses': money(period.projected_expenses),
        'projectedGrossProfit': money(period.projected_gross_profit),
        'projectedNetProfit': money(period.projected_net_profit),
        'projectedCashPosition': money(period.projected_cash_position),
        'projectedInventoryCost': money(period.projected_inventory_cost),
    }


def run_payload(run, periods=None, history=None):
    periods = periods if periods is not None else list(run.periods.all())
    return {
        'id': run.id,
        'method': run.method,
        'lookbackDays': run.lookback_days,
        'horizonDays': run.horizon_days,
        'periodGranularity': run.period_granularity,
        'confidence': run.confidence,
        'warnings': run.warnings,
        'assumptions': run.assumptions,
        'history': history or [],
        'periods': [period_payload(period) for period in periods],
        'summary': run.summary,
        'createdAt': run.created_at.isoformat() if run.created_at else None,
    }


def build_history(*, sales, expenses, sale_lines, cash_entries, lookback_days):
    today = timezone.localdate()
    start_date = today - timedelta(days=lookback_days - 1)
    rows = []

    for offset in range(lookback_days):
        day = start_date + timedelta(days=offset)
        day_start = timezone.make_aware(datetime.combine(day, time.min))
        day_end = day_start + timedelta(days=1)
        day_sales = sales.filter(sold_at__gte=day_start, sold_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_expenses = expenses.filter(spent_at__gte=day_start, spent_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_cogs = (
            sale_lines
            .filter(sale__sold_at__gte=day_start, sale__sold_at__lt=day_end)
            .annotate(line_cost=F('unit_cost') * F('quantity'))
            .aggregate(total=Sum('line_cost'))['total']
            or Decimal('0.00')
        )
        inventory_cost = (
            expenses
            .filter(spent_at__gte=day_start, spent_at__lt=day_end, expense_type=Expense.TYPE_INVENTORY_PURCHASE)
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )
        cash_inflow = (
            cash_entries
            .filter(occurred_at__gte=day_start, occurred_at__lt=day_end, direction=CashEntry.DIRECTION_INFLOW)
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )
        cash_outflow = (
            cash_entries
            .filter(occurred_at__gte=day_start, occurred_at__lt=day_end, direction=CashEntry.DIRECTION_OUTFLOW)
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )
        rows.append({
            'date': day,
            'sales': day_sales,
            'expenses': day_expenses,
            'cogs': day_cogs,
            'gross_profit': day_sales - day_cogs,
            'net_profit': day_sales - day_cogs - day_expenses,
            'inventory_cost': inventory_cost,
            'cash_net': cash_inflow - cash_outflow,
        })
    return rows


def project_periods(*, history, horizon_days, starting_cash):
    sales_daily = forecast_daily_value([row['sales'] for row in history])
    expenses_daily = forecast_daily_value([row['expenses'] for row in history])
    cogs_daily = forecast_daily_value([row['cogs'] for row in history])
    inventory_cost_daily = forecast_daily_value([row['inventory_cost'] for row in history])
    cash_net_daily = forecast_daily_value([max(row['cash_net'], Decimal('0.00')) for row in history]) - forecast_daily_value([max(-row['cash_net'], Decimal('0.00')) for row in history])

    projected_cash = starting_cash
    today = timezone.localdate()
    periods = []

    for offset in range(1, horizon_days + 1):
        day = today + timedelta(days=offset)
        gross_profit = sales_daily - cogs_daily
        net_profit = gross_profit - expenses_daily
        projected_cash += cash_net_daily
        periods.append(ForecastPeriod(
            period_start=day,
            period_end=day,
            projected_sales=sales_daily.quantize(Decimal('0.01')),
            projected_expenses=expenses_daily.quantize(Decimal('0.01')),
            projected_gross_profit=gross_profit.quantize(Decimal('0.01')),
            projected_net_profit=net_profit.quantize(Decimal('0.01')),
            projected_cash_position=projected_cash.quantize(Decimal('0.01')),
            projected_inventory_cost=inventory_cost_daily.quantize(Decimal('0.01')),
        ))
    return periods


def history_payload(history):
    return [
        {
            'date': row['date'].isoformat(),
            'sales': money(row['sales']),
            'expenses': money(row['expenses']),
            'grossProfit': money(row['gross_profit']),
            'netProfit': money(row['net_profit']),
            'inventoryCost': money(row['inventory_cost']),
            'cashNet': money(row['cash_net']),
        }
        for row in history
    ]


def forecast_for_business(*, business, sales, expenses, sale_lines, cash_entries, lookback_days=30, horizon_days=14, persist=False, user=None):
    lookback_days = clamp_days(lookback_days, default=30, minimum=7, maximum=365)
    horizon_days = clamp_days(horizon_days, default=14, minimum=7, maximum=90)

    if not sales.exists() and not expenses.exists() and not cash_entries.exists():
        raise ForecastDataUnavailable('Forecasting needs recorded sales or expenses first. Record transactions before using the forecast module.')

    history = build_history(
        sales=sales,
        expenses=expenses,
        sale_lines=sale_lines,
        cash_entries=cash_entries,
        lookback_days=lookback_days,
    )
    active_days = sum(1 for row in history if row['sales'] > 0 or row['expenses'] > 0 or row['cash_net'] != 0)
    warnings = []
    if active_days < 7:
        warnings.append('Fewer than 7 active transaction days are available, so this forecast has low confidence.')
    if not sale_lines.exists():
        warnings.append('Sale-line cost history is missing, so gross profit and net profit forecasts may be understated or incomplete.')
    if not expenses.exists():
        warnings.append('No expense history is available, so projected expenses are treated as zero.')

    cash_inflow = cash_entries.filter(direction=CashEntry.DIRECTION_INFLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    cash_outflow = cash_entries.filter(direction=CashEntry.DIRECTION_OUTFLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    starting_cash = business.initial_capital + cash_inflow - cash_outflow
    periods = project_periods(history=history, horizon_days=horizon_days, starting_cash=starting_cash)

    projected_sales = sum((period.projected_sales for period in periods), Decimal('0.00'))
    projected_expenses = sum((period.projected_expenses for period in periods), Decimal('0.00'))
    projected_gross_profit = sum((period.projected_gross_profit for period in periods), Decimal('0.00'))
    projected_net_profit = sum((period.projected_net_profit for period in periods), Decimal('0.00'))
    projected_inventory_cost = sum((period.projected_inventory_cost for period in periods), Decimal('0.00'))
    projected_ending_cash = periods[-1].projected_cash_position if periods else starting_cash
    assumptions = {
        'method': 'Moving average with recent trend adjustment.',
        'trendWeight': '0.50',
        'salesFloor': 'Projected sales and expense lines are floored at zero.',
        'cashPosition': 'Projected cash starts from current cash position and applies projected net cash movement.',
    }
    summary = {
        'projectedSales': money(projected_sales),
        'projectedExpenses': money(projected_expenses),
        'projectedGrossProfit': money(projected_gross_profit),
        'projectedNetProfit': money(projected_net_profit),
        'projectedInventoryCost': money(projected_inventory_cost),
        'projectedEndingCash': money(projected_ending_cash),
    }
    run = ForecastRun(
        business=business,
        method=ForecastRun.METHOD_MOVING_AVERAGE_TREND,
        lookback_days=lookback_days,
        horizon_days=horizon_days,
        confidence=confidence_for_history(active_days=active_days, lookback_days=lookback_days, warnings=warnings),
        warnings=warnings,
        assumptions=assumptions,
        summary=summary,
        created_by=user,
    )

    if persist:
        run.save()
        for period in periods:
            period.forecast_run = run
        ForecastPeriod.objects.bulk_create(periods)
        periods = list(run.periods.all())

    return run_payload(run, periods=periods, history=history_payload(history))
