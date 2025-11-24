import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_POST

from blog.utils.openai_review import review_blog_content
from .models import BlogPage, Like

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def like_blogpage(request, page_id):
    blogpage = get_object_or_404(BlogPage, id=page_id)
    ip_address = request.META.get('REMOTE_ADDR')

    like, created = Like.objects.get_or_create(blogpage=blogpage, ip_address=ip_address)

    if like.count < 999:
        like.count += 1
        like.save()

    return JsonResponse({'likes': blogpage.get_like_count()})


@login_required
@require_POST
def draft_review(request, page_id):
    """Return an AI review for the latest draft of the page."""
    page = get_object_or_404(BlogPage, id=page_id)

    # Ensure the user can edit this page inside Wagtail admin
    perms = page.permissions_for_user(request.user)
    if not (perms.can_edit() or perms.can_publish()):
        return JsonResponse({"error": "このページをレビューする権限がありません"}, status=403)

    # Grab the latest draft (fallback to current instance)
    try:
        page_for_review = page.get_latest_revision_as_page()
    except Exception:
        page_for_review = page.specific

    content = str(getattr(page_for_review, "body", ""))
    if not content:
        return JsonResponse({"error": "本文が空のためレビューできません"}, status=400)

    try:
        review = review_blog_content(content)
    except Exception as exc:
        logger.exception("AI draft review failed for page %s", page_id)
        return JsonResponse({"error": f"AIレビューの取得に失敗しました: {exc}"}, status=502)

    return JsonResponse({"review": review})
