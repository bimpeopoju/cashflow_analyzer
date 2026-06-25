from django.db import transaction
from django.utils import timezone

from finance.models import CashEntry, Expense


@transaction.atomic
def create_expense(*, business, payload, user=None):
    expense = Expense.objects.create(business=business, created_by=user, **payload)
    if expense.payment_status == Expense.PAYMENT_PAID and expense.amount > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_EXPENSE_PAYMENT,
            direction=CashEntry.DIRECTION_OUTFLOW,
            amount=expense.amount,
            occurred_at=expense.spent_at,
            reference_type='expense',
            reference_id=expense.id,
            note=expense.note,
        )
    return expense


@transaction.atomic
def void_expense(*, business, pk, user=None, reason=''):
    expense = (
        Expense.objects
        .select_for_update()
        .filter(business=business, pk=pk, status=Expense.STATUS_APPROVED)
        .first()
    )
    if expense is None:
        return False

    expense.status = Expense.STATUS_VOIDED
    expense.voided_at = timezone.now()
    expense.voided_by = user
    expense.void_reason = reason
    expense.save(update_fields=['status', 'voided_at', 'voided_by', 'void_reason'])

    if expense.payment_status == Expense.PAYMENT_PAID and expense.amount > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_EXPENSE_PAYMENT,
            direction=CashEntry.DIRECTION_INFLOW,
            amount=expense.amount,
            occurred_at=timezone.now(),
            reference_type='expense_void',
            reference_id=expense.id,
            note=reason or f'Voided expense #{expense.id}',
        )
    return True
