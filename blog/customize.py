from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied
from wagtail.admin.utils import get_valid_next_url_from_request
from wagtail.models import Page


# 管理画面で編集者はブログ記事の追加しかできないように他のメニューは非表示する。
def custom_add_subpage(request, parent_page_id):
    parent_page = get_object_or_404(Page, id=parent_page_id).specific
    if not parent_page.permissions_for_user(request.user).can_add_subpage():
        raise PermissionDenied

    page_types = [
        (
            model.get_verbose_name(),
            model._meta.app_label,
            model._meta.model_name,
            model.get_page_description(),
        )
        for model in type(parent_page).creatable_subpage_models()
        if model.can_create_at(parent_page)
    ]

    # `editor` グループのユーザーは `BlogPage` のみ表示
    if request.user.groups.filter(name="Editors").exists():
        page_types = [page_type for page_type in page_types if page_type[2] == "blogpage"]

    page_types.sort(key=lambda page_type: page_type[0].lower())

    if len(page_types) == 1:
        verbose_name, app_label, model_name, description = page_types[0]
        return redirect("wagtailadmin_pages:add", app_label, model_name, parent_page.id)

    return TemplateResponse(
        request,
        "wagtailadmin/pages/add_subpage.html",
        {
            "parent_page": parent_page,
            "page_types": page_types,
            "next": get_valid_next_url_from_request(request),
        },
    )