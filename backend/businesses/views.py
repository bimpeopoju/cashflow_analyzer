import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from finance.models import BusinessMembership
from finance.serializers import validate_business_payload
from finance.services import business_payload, create_business_for_user
from finance.selectors import list_user_businesses


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
