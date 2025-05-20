from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from mysite.settings.google_email_whitelist import get_allowed_emails

allowed = get_allowed_emails()
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email
        if email not in allowed:
            raise PermissionDenied("このGoogleアカウントではログインできません。")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        email = user.email

        if email in allowed:
            user.is_staff = True
            user.save()

            editors_group, _ = Group.objects.get_or_create(name="Editors")
            user.groups.add(editors_group)

        return user