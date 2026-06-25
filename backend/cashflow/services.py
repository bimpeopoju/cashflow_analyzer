from decimal import Decimal

from django.utils import timezone

from cashflow.calculations import capital_summary_for_business
from cashflow.models import CashEntry


def create_capital_entry(*, business, payload, user=None):
    if payload['entry_type'] == CashEntry.ENTRY_OWNER_WITHDRAWAL:
        summary = capital_summary_for_business(business=business)['summary']
        available_profit = Decimal(summary['availableProfit'])
        if payload['amount'] > available_profit:
            raise ValueError('Withdrawal exceeds available profit and would erode capital.')

    return CashEntry.objects.create(
        business=business,
        entry_type=payload['entry_type'],
        direction=payload['direction'],
        amount=payload['amount'],
        occurred_at=timezone.now(),
        reference_type='capital',
        reference_id=None,
        note=payload['note'],
    )
