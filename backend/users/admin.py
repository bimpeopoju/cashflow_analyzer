from django.contrib import admin

from .models import OAuthIdentity


@admin.register(OAuthIdentity)
class OAuthIdentityAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'email', 'created_at', 'updated_at')
    list_filter = ('provider',)
    search_fields = ('user__email', 'email', 'subject')
