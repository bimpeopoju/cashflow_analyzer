from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from businesses.services import get_business_for_user
from cashflow.selectors import cash_entries_for_business
from expenses.selectors import expenses_for_business
from forecasting.calculations import ForecastDataUnavailable, forecast_for_business
from forecasting.serializers import forecast_params_from_request
from sales.selectors import sale_lines_for_business, sales_for_business


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
def forecast_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response

    try:
        params = forecast_params_from_request(request)
        forecast = forecast_for_business(
            business=business,
            sales=sales_for_business(business),
            expenses=expenses_for_business(business),
            sale_lines=sale_lines_for_business(business),
            cash_entries=cash_entries_for_business(business),
            persist=request.method == 'POST',
            user=request.user if request.method == 'POST' else None,
            **params,
        )
    except ForecastDataUnavailable as exc:
        return JsonResponse({
            'message': str(exc),
            'code': 'forecast_data_unavailable',
        }, status=409)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)

    return JsonResponse({'forecast': forecast}, status=201 if request.method == 'POST' else 200)
