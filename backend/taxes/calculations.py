from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from businesses.services import money
from taxes.models import TaxEstimate, TaxRule


class TaxDataUnavailable(ValueError):
    pass


def rule_payload(rule):
    return {
        'code': rule.code,
        'name': rule.name,
        'taxType': rule.tax_type,
        'rate': str(rule.rate),
        'thresholdMin': money(rule.threshold_min) if rule.threshold_min is not None else None,
        'thresholdMax': money(rule.threshold_max) if rule.threshold_max is not None else None,
        'effectiveFrom': rule.effective_from.isoformat(),
        'effectiveTo': rule.effective_to.isoformat() if rule.effective_to else None,
        'sourceUrl': rule.source_url,
        'notes': rule.notes,
    }


def active_rules_for_period(period_end):
    return TaxRule.objects.filter(
        is_active=True,
        effective_from__lte=period_end,
    ).filter(
        effective_to__isnull=True,
    ) | TaxRule.objects.filter(
        is_active=True,
        effective_from__lte=period_end,
        effective_to__gte=period_end,
    )


def select_cit_rule(*, rules, gross_turnover):
    cit_rules = [rule for rule in rules if rule.tax_type == TaxRule.TYPE_CIT]
    for rule in cit_rules:
        min_ok = rule.threshold_min is None or gross_turnover >= rule.threshold_min
        max_ok = rule.threshold_max is None or gross_turnover <= rule.threshold_max
        if min_ok and max_ok:
            return rule
    return None


def select_vat_rule(rules):
    return next((rule for rule in rules if rule.tax_type == TaxRule.TYPE_VAT), None)


def default_period():
    today = timezone.localdate()
    return today - timedelta(days=29), today


def period_bounds(period_start, period_end):
    start = timezone.make_aware(datetime.combine(period_start, time.min))
    end = timezone.make_aware(datetime.combine(period_end + timedelta(days=1), time.min))
    return start, end


def estimate_tax_for_business(*, business, sales, expenses, sale_lines, period_start=None, period_end=None, persist=False):
    period_start, period_end = (period_start, period_end) if period_start and period_end else default_period()
    start, end = period_bounds(period_start, period_end)

    period_sales = sales.filter(sold_at__gte=start, sold_at__lt=end)
    period_expenses = expenses.filter(spent_at__gte=start, spent_at__lt=end)
    period_sale_lines = sale_lines.filter(sale__sold_at__gte=start, sale__sold_at__lt=end)

    if not period_sales.exists() and not period_expenses.exists():
        raise TaxDataUnavailable('Tax estimates need recorded sales or expenses first. Record transactions before using the tax calculator.')

    gross_sales = period_sales.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    deductible_expenses = period_expenses.exclude(expense_type='personal_withdrawal').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    cost_of_goods_sold = (
        period_sale_lines.annotate(line_cost=F('unit_cost') * F('quantity'))
        .aggregate(total=Sum('line_cost'))['total']
        or Decimal('0.00')
    )

    rules = list(active_rules_for_period(period_end))
    vat_rule = select_vat_rule(rules)
    cit_rule = select_cit_rule(rules=rules, gross_turnover=gross_sales)

    vat_rate = vat_rule.rate if vat_rule else Decimal('0.0000')
    output_vat = (gross_sales * vat_rate).quantize(Decimal('0.01'))
    input_vat = Decimal('0.00')
    net_vat_payable = max(output_vat - input_vat, Decimal('0.00'))
    taxable_profit = max(gross_sales - cost_of_goods_sold - deductible_expenses, Decimal('0.00'))
    income_tax = (taxable_profit * cit_rule.rate).quantize(Decimal('0.01')) if cit_rule else Decimal('0.00')
    total_estimated_tax = net_vat_payable + income_tax

    assumptions = {
        'scope': 'Nigeria FIRS/NRS estimate, not a filed return.',
        'vatTreatment': 'All recorded sales are treated as standard-rated VAT-exclusive supplies until transaction tax categories are added.',
        'inputVatTreatment': 'Input VAT is currently treated as zero because expenses do not yet capture VAT claimability.',
        'incomeTaxTreatment': 'Taxable profit is estimated as sales minus COGS and non-withdrawal expenses.',
        'entityTreatment': 'Company income tax rules are applied by turnover band; unincorporated trader PIT is not implemented yet.',
    }
    rule_snapshot = {
        'vat': rule_payload(vat_rule) if vat_rule else None,
        'incomeTax': rule_payload(cit_rule) if cit_rule else None,
    }
    result = {
        'grossSales': money(gross_sales),
        'costOfGoodsSold': money(cost_of_goods_sold),
        'deductibleExpenses': money(deductible_expenses),
        'taxableProfit': money(taxable_profit),
        'outputVat': money(output_vat),
        'inputVat': money(input_vat),
        'netVatPayable': money(net_vat_payable),
        'incomeTax': money(income_tax),
        'totalEstimatedTax': money(total_estimated_tax),
    }

    estimate = None
    if persist:
        estimate = TaxEstimate.objects.create(
            business=business,
            period_start=period_start,
            period_end=period_end,
            rule_snapshot=rule_snapshot,
            assumptions=assumptions,
            result=result,
        )

    return {
        'id': estimate.id if estimate else None,
        'period': {
            'startDate': period_start.isoformat(),
            'endDate': period_end.isoformat(),
        },
        'rules': rule_snapshot,
        'assumptions': assumptions,
        'result': result,
        'createdAt': estimate.created_at.isoformat() if estimate else None,
    }
