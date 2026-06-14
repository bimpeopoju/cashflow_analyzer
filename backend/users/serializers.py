from decimal import Decimal

from rest_framework import serializers

from finance.models import BusinessProfile


def money(value):
    return str((value or Decimal('0.00')).quantize(Decimal('0.01')))


def serialize_user(user):
    profile, _ = BusinessProfile.objects.get_or_create(
        user=user,
        defaults={
            'business_name': f"{user.first_name or 'MarketFlow'} Business",
            'stall_name': 'Market stall',
        },
    )
    return {
        'id': user.id,
        'email': user.email,
        'fullName': user.get_full_name() or user.username,
        'businessName': profile.business_name,
        'stallName': profile.stall_name,
        'initialCapital': money(profile.initial_capital),
    }


class RegisterSerializer(serializers.Serializer):
    fullName = serializers.CharField(source='full_name', max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=False)
