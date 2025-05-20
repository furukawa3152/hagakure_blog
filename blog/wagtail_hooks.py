from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from django.templatetags.static import static
from django.utils.html import format_html


@hooks.register("construct_explorer_page_queryset")
def restrict_editor_subpages(parent_page, queryset, request):
    """Editor 権限のユーザーは Blog Page 以外を見れないようにする"""
    if request.user.groups.filter(name="Editor").exists():
        return queryset.filter(content_type__model="blogpage")
    return queryset  # それ以外のユーザーはそのまま


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    """Add /static/js/admin/easymde_custom.js to the admin."""
    return format_html('<script src="{}"></script>', static("js/easymde_custom.js"))
