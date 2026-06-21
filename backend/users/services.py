from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ValidationError as SerializerValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from finance.services import create_business_for_user


User = get_user_model()


def normalize_email(email):
    return User.objects.normalize_email(email).lower()


def token_pair_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@transaction.atomic
def register_user(*, full_name, email, password):
    normalized_email = normalize_email(email)
    if User.objects.filter(username__iexact=normalized_email).exists():
        raise SerializerValidationError({
            'email': ['An account with that email already exists.'],
        })

    first_name, _, last_name = full_name.strip().partition(' ')
    candidate = User(
        username=normalized_email,
        email=normalized_email,
        first_name=first_name,
        last_name=last_name,
    )
    try:
        password_validation.validate_password(password, user=candidate)
    except ValidationError as exc:
        raise SerializerValidationError({'password': list(exc.messages)}) from exc

    candidate.set_password(password)
    candidate.save()
    create_business_for_user(
        user=candidate,
        name=f'{first_name or "MarketFlow"} Business',
        stall_name='Market stall',
        initial_capital=Decimal('100000.00'),
    )
    return candidate


def authenticate_user(*, request, email, password):
    user = authenticate(
        request=request,
        username=normalize_email(email),
        password=password,
    )
    if user is None or not user.is_active:
        raise AuthenticationFailed('Invalid email or password.')
    return user
