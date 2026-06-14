from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthenticationMiddleware:
    """Authenticate bearer tokens for legacy Django views during migration."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        if not request.user.is_authenticated:
            try:
                authenticated = self.jwt_authentication.authenticate(request)
            except (AuthenticationFailed, InvalidToken):
                authenticated = None

            if authenticated is not None:
                request.user, request.auth = authenticated
            elif not hasattr(request, 'user'):
                request.user = AnonymousUser()

        return self.get_response(request)
