from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def google_oauth_configured():
    google_app = (
        settings.SOCIALACCOUNT_PROVIDERS
        .get("google", {})
        .get("APP", {})
    )
    return bool(google_app.get("client_id") and google_app.get("secret"))


@register.simple_tag
def dev_login_enabled():
    return settings.DEBUG and not google_oauth_configured()
