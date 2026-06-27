from datetime import datetime


def parse_date(value, field_name):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f'{field_name} must use YYYY-MM-DD format.') from None


def period_from_request(request):
    start = parse_date(request.GET.get('start'), 'start')
    end = parse_date(request.GET.get('end'), 'end')
    if (start and not end) or (end and not start):
        raise ValueError('Both start and end are required when filtering by date.')
    if start and end and start > end:
        raise ValueError('start cannot be after end.')
    return start, end
