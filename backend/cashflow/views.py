import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from businesses.services import get_business_for_user
from cashflow.calculations import capital_summary_for_business
from cashflow.models import CashEntry
from cashflow.serializers import cash_entry_payload, validate_cash_entry_payload
from cashflow.services import create_capital_entry


def require_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Authentication required.'}, status=401)
    return None


def resolve_business_or_response(request, business_id=None):
    business = get_business_for_user(request.user, business_id)
    if business is None:
        return None, JsonResponse({'message': 'Business not found.'}, status=404)
    return business, None


def read_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def capital_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response

    entries = CashEntry.objects.filter(business=business)
    if request.method == 'GET':
        return JsonResponse({
            'entries': [cash_entry_payload(entry) for entry in entries[:50]],
            **capital_summary_for_business(business=business, cash_entries=entries),
        })

    try:
        payload = validate_cash_entry_payload(read_json(request))
        entry = create_capital_entry(business=business, payload=payload, user=request.user)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)

    refreshed_entries = CashEntry.objects.filter(business=business)
    return JsonResponse({
        'entry': cash_entry_payload(entry),
        **capital_summary_for_business(business=business, cash_entries=refreshed_entries),
    }, status=201)
