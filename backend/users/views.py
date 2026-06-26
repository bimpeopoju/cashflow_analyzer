from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, LogoutSerializer, RegisterSerializer, serialize_user
from .services import authenticate_user, register_user, token_pair_for_user


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        return Response(
            {'user': serialize_user(user), 'tokens': token_pair_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate_user(request=request, **serializer.validated_data)
        return Response({'user': serialize_user(user), 'tokens': token_pair_for_user(user)})


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_value = serializer.validated_data.get('refresh')
        if refresh_value:
            try:
                RefreshToken(refresh_value).blacklist()
            except TokenError:
                return Response(
                    {'message': 'Refresh token is invalid or expired.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response({'message': 'Signed out.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'user': serialize_user(request.user)})


class OAuthProviderListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        providers = [
            {
                'id': provider_id,
                'label': configuration['label'],
                'enabled': configuration['enabled'],
            }
            for provider_id, configuration in settings.OAUTH_PROVIDERS.items()
        ]
        return Response({'providers': providers})
