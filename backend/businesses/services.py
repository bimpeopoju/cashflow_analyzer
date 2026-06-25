from decimal import Decimal

from django.db import transaction

from businesses.models import Business, BusinessMembership, BusinessProfile


def money(value):
    return str((value or Decimal('0.00')).quantize(Decimal('0.01')))


def business_payload(business, role=None):
    return {
        'id': business.id,
        'name': business.name,
        'stallName': business.stall_name,
        'initialCapital': money(business.initial_capital),
        'role': role,
    }


@transaction.atomic
def create_business_for_user(
    *,
    user,
    name,
    stall_name='Market stall',
    initial_capital=Decimal('0.00'),
):
    business = Business.objects.create(
        owner=user,
        name=name,
        stall_name=stall_name,
        initial_capital=initial_capital,
    )
    BusinessMembership.objects.create(
        business=business,
        user=user,
        role=BusinessMembership.ROLE_OWNER,
        status=BusinessMembership.STATUS_ACTIVE,
    )
    BusinessProfile.objects.get_or_create(
        user=user,
        defaults={
            'business_name': name,
            'stall_name': stall_name,
            'initial_capital': initial_capital,
        },
    )
    return business


def active_memberships_for_user(user):
    ensure_default_business(user)
    return (
        BusinessMembership.objects
        .filter(user=user, status=BusinessMembership.STATUS_ACTIVE)
        .select_related('business')
        .order_by('business__name', 'id')
    )


def ensure_default_business(user):
    membership = (
        BusinessMembership.objects
        .filter(user=user, status=BusinessMembership.STATUS_ACTIVE)
        .select_related('business')
        .order_by('business__name', 'id')
        .first()
    )
    if membership:
        return membership.business

    profile, _ = BusinessProfile.objects.get_or_create(
        user=user,
        defaults={
            'business_name': f"{user.first_name or 'MarketFlow'} Business",
            'stall_name': 'Market stall',
        },
    )
    return create_business_for_user(
        user=user,
        name=profile.business_name,
        stall_name=profile.stall_name or 'Market stall',
        initial_capital=profile.initial_capital,
    )


def get_business_for_user(user, business_id=None):
    if business_id is None:
        return ensure_default_business(user)

    membership = (
        BusinessMembership.objects
        .filter(
            user=user,
            business_id=business_id,
            status=BusinessMembership.STATUS_ACTIVE,
        )
        .select_related('business')
        .first()
    )
    return membership.business if membership else None
