import json
from datetime import datetime, time, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from users.serializers import serialize_user

from .models import BusinessMembership, Expense, InventoryItem, Sale
from .services import (
    active_memberships_for_user,
    business_payload,
    create_business_for_user,
    get_business_for_user,
    money,
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


def decimal_from_payload(data, field):
    try:
        value = Decimal(str(data.get(field, '0'))).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field} must be a valid amount.')
    if value < 0:
        raise ValueError(f'{field} cannot be negative.')
    return value


def int_from_payload(data, field, default=0):
    try:
        value = int(data.get(field, default))
    except (TypeError, ValueError):
        raise ValueError(f'{field} must be a whole number.')
    if value < 0:
        raise ValueError(f'{field} cannot be negative.')
    return value


def text_from_payload(data, field, label, required=True):
    value = str(data.get(field, '')).strip()
    if required and not value:
        raise ValueError(f'{label} is required.')
    return value


def sale_payload(sale):
    return {
        'id': sale.id,
        'itemName': sale.item_name,
        'amount': money(sale.amount),
        'quantity': sale.quantity,
        'note': sale.note,
        'createdAt': sale.sold_at.isoformat(),
    }


def expense_payload(expense):
    return {
        'id': expense.id,
        'category': expense.category,
        'amount': money(expense.amount),
        'note': expense.note,
        'createdAt': expense.spent_at.isoformat(),
    }


def inventory_payload(item):
    return {
        'id': item.id,
        'name': item.name,
        'quantity': item.quantity,
        'unit': item.unit,
        'reorderLevel': item.reorder_level,
        'unitCost': money(item.unit_cost),
        'stockValue': money(item.unit_cost * item.quantity),
    }


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
        memberships = active_memberships_for_user(request.user)
        return JsonResponse({
            'businesses': [
                business_payload(membership.business, membership.role)
                for membership in memberships
            ],
        })

    try:
        data = read_json(request)
        business = create_business_for_user(
            user=request.user,
            name=text_from_payload(data, 'name', 'Business name'),
            stall_name=text_from_payload(data, 'stallName', 'Stall name', required=False) or 'Market stall',
            initial_capital=decimal_from_payload(data, 'initialCapital'),
        )
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

    today = timezone.localdate()
    start = timezone.make_aware(datetime.combine(today, time.min))
    week_start = start - timedelta(days=6)

    sales = Sale.objects.filter(business=business)
    expenses = Expense.objects.filter(business=business)
    inventory = InventoryItem.objects.filter(business=business)

    sales_today = sales.filter(sold_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expenses_today = expenses.filter(spent_at__gte=start).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_sales = sales.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    net_profit = total_sales - total_expenses

    recent = [
        {
            'id': f'sale-{sale.id}',
            'kind': 'sale',
            'label': sale.item_name,
            'amount': money(sale.amount),
            'createdAt': sale.sold_at.isoformat(),
        }
        for sale in sales[:5]
    ] + [
        {
            'id': f'expense-{expense.id}',
            'kind': 'expense',
            'label': expense.category,
            'amount': money(expense.amount),
            'createdAt': expense.spent_at.isoformat(),
        }
        for expense in expenses[:5]
    ]
    recent.sort(key=lambda item: item['createdAt'], reverse=True)

    weekly = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        day_start = timezone.make_aware(datetime.combine(day, time.min))
        day_end = day_start + timedelta(days=1)
        day_sales = sales.filter(sold_at__gte=day_start, sold_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        day_expenses = expenses.filter(spent_at__gte=day_start, spent_at__lt=day_end).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        weekly.append({
            'day': day.strftime('%a'),
            'sales': money(day_sales),
            'expenses': money(day_expenses),
        })

    low_stock = [
        inventory_payload(item)
        for item in inventory
        if item.quantity <= item.reorder_level
    ][:5]

    top_sale = sales.filter(sold_at__gte=week_start).values('item_name').annotate(total=Sum('amount')).order_by('-total').first()

    return JsonResponse({
        'user': serialize_user(request.user),
        'summary': {
            'salesToday': money(sales_today),
            'expensesToday': money(expenses_today),
            'netProfit': money(net_profit),
            'transactionsToday': sales.filter(sold_at__gte=start).count() + expenses.filter(spent_at__gte=start).count(),
            'initialCapital': money(business.initial_capital),
            'currentCapital': money(business.initial_capital + net_profit),
            'inventoryValue': money(sum((item.unit_cost * item.quantity for item in inventory), Decimal('0.00'))),
        },
        'recentActivity': recent[:6],
        'lowStock': low_stock,
        'topSelling': {
            'name': top_sale['item_name'] if top_sale else 'No sales yet',
            'amount': money(top_sale['total']) if top_sale else '0.00',
        },
        'weeklyPerformance': weekly,
    })


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
        return JsonResponse({'sales': [sale_payload(sale) for sale in Sale.objects.filter(business=business)[:50]]})

    try:
        data = read_json(request)
        sale = Sale.objects.create(
            business=business,
            item_name=text_from_payload(data, 'itemName', 'Item name'),
            amount=decimal_from_payload(data, 'amount'),
            quantity=int_from_payload(data, 'quantity', 1),
            note=text_from_payload(data, 'note', 'Note', required=False),
        )
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
    Sale.objects.filter(business=business, pk=pk).delete()
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
        return JsonResponse({'expenses': [expense_payload(expense) for expense in Expense.objects.filter(business=business)[:50]]})

    try:
        data = read_json(request)
        expense = Expense.objects.create(
            business=business,
            category=text_from_payload(data, 'category', 'Category'),
            amount=decimal_from_payload(data, 'amount'),
            note=text_from_payload(data, 'note', 'Note', required=False),
        )
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
    Expense.objects.filter(business=business, pk=pk).delete()
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
        return JsonResponse({'items': [inventory_payload(item) for item in InventoryItem.objects.filter(business=business)[:100]]})

    try:
        data = read_json(request)
        item = InventoryItem.objects.create(
            business=business,
            name=text_from_payload(data, 'name', 'Item name'),
            quantity=int_from_payload(data, 'quantity', 0),
            unit=text_from_payload(data, 'unit', 'Unit', required=False) or 'pcs',
            reorder_level=int_from_payload(data, 'reorderLevel', 5),
            unit_cost=decimal_from_payload(data, 'unitCost'),
        )
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
    InventoryItem.objects.filter(business=business, pk=pk).delete()
    return JsonResponse({'message': 'Inventory item deleted.'})
