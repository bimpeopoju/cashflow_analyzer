import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from finance.services import get_business_for_user
from inventory.services import create_inventory_item, void_inventory_item
from inventory.selectors import inventory_for_business
from inventory.serializers import inventory_payload, validate_inventory_payload, validate_void_payload


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
def inventory_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    if request.method == 'GET':
        return JsonResponse({'items': [inventory_payload(item) for item in inventory_for_business(business)[:100]]})
    try:
        item = create_inventory_item(business=business, payload=validate_inventory_payload(read_json(request)), user=request.user)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)
    return JsonResponse({'item': inventory_payload(item)}, status=201)


@csrf_exempt
@require_http_methods(['DELETE'])
def inventory_detail_view(request, pk, business_id=None):
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
    void_inventory_item(business=business, pk=pk, user=request.user, reason=payload['reason'])
    return JsonResponse({'message': 'Inventory item voided.'})
