import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from finance.services import get_business_for_user
from expenses.selectors import expenses_for_business
from expenses.services import create_expense, void_expense
from expenses.serializers import expense_payload, validate_expense_payload, validate_void_payload


def read_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError('Request body must be valid JSON.')


def require_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Authentication required.'}, status=401)
    return None


def resolve_business_or_response(request, business_id=None):
    business = get_business_for_user(request.user, business_id)
    if business is None:
        return None, JsonResponse({'message': 'Business not found.'}, status=404)
    return business, None


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def expenses_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    if request.method == 'GET':
        return JsonResponse({'expenses': [expense_payload(expense) for expense in expenses_for_business(business)[:50]]})
    try:
        expense = create_expense(business=business, payload=validate_expense_payload(read_json(request)), user=request.user)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)
    return JsonResponse({'expense': expense_payload(expense)}, status=201)


@csrf_exempt
@require_http_methods(['DELETE'])
def expense_detail_view(request, pk, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    try:
        payload = validate_void_payload(read_json(request))
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)
    void_expense(business=business, pk=pk, user=request.user, reason=payload['reason'])
    return JsonResponse({'message': 'Expense voided.'})
