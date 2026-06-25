from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from finance.services import get_business_for_user
from reports.calculations import dashboard_for_business
from reports.selectors import cash_entries_for_business, expenses_for_business, inventory_for_business, sale_lines_for_business, sales_for_business
from users.serializers import serialize_user


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
def reports_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    dashboard = dashboard_for_business(
        business=business,
        sales=sales_for_business(business),
        expenses=expenses_for_business(business),
        inventory=inventory_for_business(business),
        sale_lines=sale_lines_for_business(business),
        cash_entries=cash_entries_for_business(business),
    )
    return JsonResponse({'user': serialize_user(request.user), **dashboard})
