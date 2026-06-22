from .models import BusinessMembership


def get_active_membership(user, business_id):
    return (
        BusinessMembership.objects
        .filter(
            user=user,
            business_id=business_id,
            status=BusinessMembership.STATUS_ACTIVE,
        )
        .select_related('business')
        .first()
    )


def user_can_access_business(user, business_id):
    return get_active_membership(user, business_id) is not None
