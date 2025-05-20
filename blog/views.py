from django.http import JsonResponse

from .models import BlogPage, Like
from django.shortcuts import get_object_or_404, render

from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def like_blogpage(request, page_id):
    blogpage = get_object_or_404(BlogPage, id=page_id)
    ip_address = request.META.get('REMOTE_ADDR')

    like, created = Like.objects.get_or_create(blogpage=blogpage, ip_address=ip_address)

    if like.count < 999:
        like.count += 1
        like.save()

    return JsonResponse({'likes': blogpage.get_like_count()})

