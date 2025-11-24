from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from wagtail.models import Page


@hooks.register("construct_explorer_page_queryset")
def restrict_editor_subpages(parent_page, queryset, request):
    """Editor 権限のユーザーは Blog Page 以外を見れないようにする"""
    if request.user.groups.filter(name="Editor").exists():
        return queryset.filter(content_type__model="blogpage")
    return queryset  # それ以外のユーザーはそのまま


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    """Add /static/js/admin/easymde_custom.js to the admin."""
    return format_html(
        '<script src="{}"></script><script src="{}"></script>',
        static("js/easymde_custom.js"),
        static("js/admin/draft_review.js"),
    )


@hooks.register("insert_editor_js", order=110)
def editor_only_js():
    """Ensure draft review button script loads on editor views."""
    return format_html('<script src="{}"></script>', static("js/admin/draft_review.js"))


@hooks.register("register_page_action_buttons")
def add_draft_review_button(page, page_perms, is_parent=False, next_url=None):
    """Show AI review button on page edit (handled by JS fetch)."""
    from blog.models import BlogPage

    if isinstance(page, BlogPage):
        class DraftReviewButton(Component):
            order = 40

            def render_html(self, parent_context=None):
                return format_html(
                    '<button type="button" class="button button-secondary draft-review-button" data-draft-review-button="{id}">下書きをAIレビュー</button>',
                    id=page.id,
                )

        yield DraftReviewButton()


@hooks.register("register_admin_urls")
def register_admin_urls():
    from blog import views

    return [
        path("api/draft-review/<int:page_id>/", views.draft_review, name="draft_review"),
    ]
