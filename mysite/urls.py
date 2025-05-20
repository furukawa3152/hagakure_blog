from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
#from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from blog.customize import custom_add_subpage  # 編集者権限の非表示機能のカスタマイズ

from blog import views # いいね
from home import views as home
from mysite import views as mysite


urlpatterns = [
    # CMS以外
    path('', home.index, name='index'),
    path('voice/', home.voice, name='voice'),
    path('saga_bot/', home.saga_bot, name='saga_bot'),
    path('trans_sagaben/', home.trans_sagaben, name='trans_sagaben'),
    path('indext5explain/', home.indext5explain, name='indext5explain'),
    path('term_use/', home.term_use, name='term_use'),
    
    # CMS
    path('blog_guidelines/', mysite.blog_guidelines, name='blog_guidelines'),
    # path('login/', mysite.tem.login, name='blog_login'),
    #以下アドミンページを一旦コメントアウト
    path('admin/pages/<int:parent_page_id>/add_subpage/', custom_add_subpage, name='wagtailadmin_pages:add_subpage'), # 編集者権限の非表示機能のオーバライド
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("search/", search_views.search, name="search"),
    path('like/<int:page_id>/', views.like_blogpage, name='like_blogpage'),
    path("accounts/", include("allauth.urls")),  # GoogleログインURLを追加
    
    
    # 404テスト用
    #path("test404/", mysite.test_404),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    #For anything not caught by a more specific rule above, hand over to
    #Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('',include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

#Debug=Falseの時にエラーをHTMLで表示させるロジック
#handler500 = 'mysite.views.custom_500_view'