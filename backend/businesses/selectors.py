from finance.models import BusinessMembership
from businesses.services import ensure_default_business


def list_user_businesses(user):
    ensure_default_business(user)
    return (
        BusinessMembership.objects
        .filter(user=user, status=BusinessMembership.STATUS_ACTIVE)
        .select_related('business')
        .order_by('business__name', 'id')
    )


def default_business_for_user(user):
    return ensure_default_business(user)
