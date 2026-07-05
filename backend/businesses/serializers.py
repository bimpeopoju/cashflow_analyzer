from datetime import date
from decimal import Decimal, InvalidOperation

from businesses.services import business_payload


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


def boolean_from_payload(data, field, label):
    value = data.get(field)
    if isinstance(value, bool):
        return value
    if value in ('true', '1', 1):
        return True
    if value in ('false', '0', 0):
        return False
    raise ValueError(f'{label} must be true or false.')


def validate_business_payload(data):
    return {
        'name': text_from_payload(data, 'name', 'Business name'),
        'stall_name': text_from_payload(data, 'stallName', 'Stall name', required=False) or 'Market stall',
        'initial_capital': decimal_from_payload(data, 'initialCapital'),
    }


def validate_tax_profile_payload(data):
    tin = text_from_payload(data, 'tin', 'Tax Identification Number', required=False).upper().replace(' ', '')
    entity_type = text_from_payload(data, 'entityType', 'Entity type', required=False)
    if entity_type and entity_type not in {
        'company',
        'sole_proprietor',
        'partnership',
    }:
        raise ValueError('Entity type is invalid.')

    vat_registered = boolean_from_payload(data, 'vatRegistered', 'VAT registered')
    month = data.get('accountingYearEndMonth')
    day = data.get('accountingYearEndDay')
    if month in ('', None) and day in ('', None):
        accounting_year_end_month = None
        accounting_year_end_day = None
    else:
        try:
            accounting_year_end_month = int(month)
            accounting_year_end_day = int(day)
        except (TypeError, ValueError):
            raise ValueError('Accounting year end must include a valid month and day.') from None
        try:
            date(2023, accounting_year_end_month, accounting_year_end_day)
        except ValueError:
            raise ValueError('Accounting year end is not a valid calendar date.') from None

    return {
        'tin': tin,
        'entity_type': entity_type,
        'vat_registered': vat_registered,
        'accounting_year_end_month': accounting_year_end_month,
        'accounting_year_end_day': accounting_year_end_day,
    }
