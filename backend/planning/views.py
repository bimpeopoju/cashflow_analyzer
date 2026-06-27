from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from businesses.services import get_business_for_user
from inventory.selectors import inventory_for_business, stock_movements_for_business
from planning.calculations import burn_rate_for_business


def require_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Authentication required.'}, status=401)
    return None


def resolve_business_or_response(request, business_id=None):
    business = get_business_for_user(request.user, business_id)
    if business is None:
        return None, JsonResponse({'message': 'Business not found.'}, status=404)
    return business, None


def period_days_from_request(request):
    raw_value = request.GET.get('days', '30')
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return 30
    return min(max(value, 1), 365)


@require_http_methods(['GET'])
def burn_rate_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response

    return JsonResponse(burn_rate_for_business(
        inventory=inventory_for_business(business),
        stock_movements=stock_movements_for_business(business),
        period_days=period_days_from_request(request),
    ))
