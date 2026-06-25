from decimal import Decimal, InvalidOperation

from businesses.services import money


def decimal_from_payload(data, field):
    try:
        value = Decimal(str(data.get(field, '0'))).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field} must be a valid amount.')
    if value < 0:
        raise ValueError(f'{field} cannot be negative.')
    return value


def text_from_payload(data, field, label, required=True):
    value = str(data.get(field, '')).strip()
    if required and not value:
        raise ValueError(f'{label} is required.')
    return value


def validate_expense_payload(data):
    payment_status = str(data.get('paymentStatus', 'paid')).strip() or 'paid'
    if payment_status not in {'paid', 'unpaid'}:
        raise ValueError('paymentStatus must be paid or unpaid.')
    expense_type = str(data.get('expenseType', 'operating')).strip() or 'operating'
    allowed_types = {
        'operating',
        'inventory_purchase',
        'tax',
        'capital',
        'personal_withdrawal',
        'other',
    }
    if expense_type not in allowed_types:
        raise ValueError('expenseType is not supported.')
    return {
        'category': text_from_payload(data, 'category', 'Category'),
        'expense_type': expense_type,
        'amount': decimal_from_payload(data, 'amount'),
        'payment_status': payment_status,
        'note': text_from_payload(data, 'note', 'Note', required=False),
    }


def expense_payload(expense):
    return {
        'id': expense.id,
        'category': expense.category,
        'expenseType': expense.expense_type,
        'amount': money(expense.amount),
        'paymentStatus': expense.payment_status,
        'status': expense.status,
        'note': expense.note,
        'createdAt': expense.spent_at.isoformat(),
    }


def validate_void_payload(data):
    return {
        'reason': text_from_payload(data, 'reason', 'Reason', required=False),
    }
