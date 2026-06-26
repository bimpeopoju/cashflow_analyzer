from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, MeView, OAuthProviderListView, RegisterView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', csrf_exempt(TokenRefreshView.as_view()), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('oauth/providers/', OAuthProviderListView.as_view(), name='oauth_provider_list'),
]
