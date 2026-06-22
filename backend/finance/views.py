import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from users.serializers import serialize_user

from .calculations import dashboard_for_business
from .models import BusinessMembership
from .selectors import (
    expenses_for_business,
    cash_entries_for_business,
    inventory_for_business,
    list_user_businesses,
    sale_lines_for_business,
    sales_for_business,
)
from .serializers import (
    expense_payload,
    inventory_payload,
    sale_payload,
    validate_business_payload,
    validate_expense_payload,
    validate_inventory_payload,
    validate_sale_payload,
)
from .services import (
    business_payload,
    create_business_for_user,
    create_expense,
    create_inventory_item,
    create_sale,
    delete_expense,
    delete_inventory_item,
    delete_sale,
    get_business_for_user,
)


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
def businesses_view(request):
    auth_response = require_user(request)
    if auth_response:
        return auth_response

    if request.method == 'GET':
        return JsonResponse({
            'businesses': [
                business_payload(membership.business, membership.role)
                for membership in list_user_businesses(request.user)
            ],
        })

    try:
        payload = validate_business_payload(read_json(request))
        business = create_business_for_user(user=request.user, **payload)
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)
    return JsonResponse({'business': business_payload(business, BusinessMembership.ROLE_OWNER)}, status=201)


@require_http_methods(['GET'])
def dashboard_view(request, business_id=None):
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


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def sales_view(request, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response

    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response

    if request.method == 'GET':
        return JsonResponse({'sales': [sale_payload(sale) for sale in sales_for_business(business)[:50]]})

    try:
        sale = create_sale(business=business, payload=validate_sale_payload(read_json(request)))
    except ValueError as exc:
        return JsonResponse({'message': str(exc)}, status=400)
    return JsonResponse({'sale': sale_payload(sale)}, status=201)


@csrf_exempt
@require_http_methods(['DELETE'])
def sale_detail_view(request, pk, business_id=None):
    auth_response = require_user(request)
    if auth_response:
        return auth_response
    business, error_response = resolve_business_or_response(request, business_id)
    if error_response:
        return error_response
    delete_sale(business=business, pk=pk)
    return JsonResponse({'message': 'Sale deleted.'})


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
        expense = create_expense(business=business, payload=validate_expense_payload(read_json(request)))
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
    delete_expense(business=business, pk=pk)
    return JsonResponse({'message': 'Expense deleted.'})


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
        item = create_inventory_item(business=business, payload=validate_inventory_payload(read_json(request)))
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
    delete_inventory_item(business=business, pk=pk)
    return JsonResponse({'message': 'Inventory item deleted.'})
