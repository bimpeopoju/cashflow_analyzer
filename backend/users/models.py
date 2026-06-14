from django.conf import settings
from django.db import models


class OAuthIdentity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='oauth_identities',
    )
    provider = models.CharField(max_length=40)
    subject = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'subject'],
                name='unique_oauth_provider_subject',
            ),
            models.UniqueConstraint(
                fields=['user', 'provider'],
                name='unique_oauth_provider_per_user',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.provider}:{self.subject}'
