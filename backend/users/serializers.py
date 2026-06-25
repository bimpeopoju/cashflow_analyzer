from rest_framework import serializers

from businesses.services import ensure_default_business, money


def serialize_user(user):
    business = ensure_default_business(user)
    return {
        'id': user.id,
        'email': user.email,
        'fullName': user.get_full_name() or user.username,
        'activeBusinessId': business.id,
        'businessName': business.name,
        'stallName': business.stall_name,
        'initialCapital': money(business.initial_capital),
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
