from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from django.utils import timezone

from businesses.services import tax_profile_payload
from taxes.calculations import TaxDataUnavailable, estimate_tax_for_business


@dataclass
class TaxDeadline:
    code: str
    label: str
    due_date: date
    description: str


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def alert_payload(level, title, message):
    return {
        'level': level,
        'title': title,
        'message': message,
    }


def deadline_payload(deadline, *, today):
    days_remaining = (deadline.due_date - today).days
    if days_remaining < 0:
        status = 'overdue'
    elif days_remaining <= 7:
        status = 'urgent'
    elif days_remaining <= 21:
        status = 'upcoming'
    else:
        status = 'normal'
    return {
        'code': deadline.code,
        'label': deadline.label,
        'dueDate': deadline.due_date.isoformat(),
        'daysRemaining': days_remaining,
        'status': status,
        'description': deadline.description,
    }


def next_vat_deadline(today):
    if today.day <= 21:
        due_date = date(today.year, today.month, 21)
    else:
        next_month_anchor = add_months(date(today.year, today.month, 1), 1)
        due_date = date(next_month_anchor.year, next_month_anchor.month, 21)
    filing_period_month = add_months(date(due_date.year, due_date.month, 1), -1)
    return TaxDeadline(
        code='vat_monthly',
        label='VAT return',
        due_date=due_date,
        description=f'Estimated due date for {filing_period_month.strftime("%B %Y")} VAT filing and payment.',
    )


def latest_cit_deadline(*, today, business):
    if business.accounting_year_end_month is None or business.accounting_year_end_day is None:
        return None

    current_year_end = date(today.year, business.accounting_year_end_month, business.accounting_year_end_day)
    if current_year_end > today:
        fiscal_year_end = date(today.year - 1, business.accounting_year_end_month, business.accounting_year_end_day)
    else:
        fiscal_year_end = current_year_end
    due_date = add_months(fiscal_year_end, 6)
    return TaxDeadline(
        code='cit_annual',
        label='Company income tax return',
        due_date=due_date,
        description=f'Estimated filing deadline for the accounting year ended {fiscal_year_end.isoformat()}.',
    )


def tax_summary_for_business(*, business, sales, expenses, sale_lines):
    today = timezone.localdate()
    profile = tax_profile_payload(business)
    deadlines = []
    alerts = []
    estimate = None

    if business.vat_registered:
        deadlines.append(deadline_payload(next_vat_deadline(today), today=today))

    if business.entity_type == business.ENTITY_COMPANY:
        cit_deadline = latest_cit_deadline(today=today, business=business)
        if cit_deadline:
            deadlines.append(deadline_payload(cit_deadline, today=today))

    if not profile['isComplete']:
        alerts.append(alert_payload(
            'warning',
            'Finish tax setup',
            'Add your TIN, entity type, and accounting year end so deadline tracking can be trusted.',
        ))

    if business.entity_type in {business.ENTITY_SOLE_PROPRIETOR, business.ENTITY_PARTNERSHIP}:
        alerts.append(alert_payload(
            'info',
            'Income tax is limited',
            'This release does not calculate personal income tax yet, so dashboard tax figures only cover VAT.',
        ))

    if deadlines and any(item['status'] == 'overdue' for item in deadlines):
        alerts.append(alert_payload(
            'critical',
            'Deadline passed',
            'One or more tax deadlines are already overdue based on the current tax setup.',
        ))
    elif deadlines and any(item['status'] == 'urgent' for item in deadlines):
        alerts.append(alert_payload(
            'warning',
            'Deadline approaching',
            'A tax deadline is due within the next 7 days.',
        ))

    try:
        estimate = estimate_tax_for_business(
            business=business,
            sales=sales,
            expenses=expenses,
            sale_lines=sale_lines,
        )
    except TaxDataUnavailable:
        alerts.append(alert_payload(
            'info',
            'No tax estimate yet',
            'Record sales or expenses before the tax preview can calculate live figures.',
        ))

    status = 'ready'
    if not profile['isComplete']:
        status = 'needs_setup'
    elif estimate is None:
        status = 'needs_activity'
    if any(item['status'] in {'overdue', 'urgent'} for item in deadlines):
        status = 'attention'

    return {
        'status': status,
        'profile': profile,
        'estimate': estimate,
        'deadlines': deadlines,
        'alerts': alerts,
        'lastUpdatedAt': timezone.now().isoformat(),
    }
