from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from businesses.services import get_business_for_user
from reports.selectors import expenses_for_business, sale_lines_for_business, sales_for_business
from taxes.calculations import TaxDataUnavailable, estimate_tax_for_business, rule_payload
from taxes.models import TaxRule
from taxes.serializers import period_from_request


def require_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Authentication required.'}, status=401)
    return None


def resolve_business_or_response(request, business_id=None):
    business = get_business_for_user(request.user, business_id)
    if business is None:
        return None, JsonResponse({'message': 'Business not found.'}, status=404)
    return business, None


@require_http_methods(['GET'])
def tax_rules_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    return JsonResponse({'rules': [rule_payload(rule) for rule in TaxRule.objects.filter(is_active=True)]})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def tax_estimate_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response

    try:
        period_start, period_end = period_from_request(request)
        estimate = estimate_tax_for_business(
            business=business,
            sales=sales_for_business(business),
            expenses=expenses_for_business(business),
            sale_lines=sale_lines_for_business(business),
            period_start=period_start,
            period_end=period_end,
            persist=request.method == 'POST',
        )
    except TaxDataUnavailable as exc:
        return JsonResponse({
            'message': str(exc),
            'code': 'tax_data_unavailable',
        }, status=409)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)

    return JsonResponse({'estimate': estimate}, status=201 if request.method == 'POST' else 200)
