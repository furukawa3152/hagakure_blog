from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.search import index

from wagtail.admin.panels import FieldPanel, InlinePanel,  MultiFieldPanel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from django.db.models import Q
from wagtail.snippets.models import register_snippet
from wagtailmarkdown.blocks import MarkdownBlock
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.exceptions import ValidationError
from wagtail.admin.forms import WagtailAdminPageForm
from wagtailcodeblock.blocks import CodeBlock
from .blocks import ImageWithCaptionBlock


# チャンネルのための追加
@register_snippet
class BlogChannel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ブログチャンネル"
        verbose_name_plural = "ブログチャンネル"



class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

import unicodedata

def count_chars(value):
    """半角文字を1、全角文字を2としてカウント"""
    count = 0
    for char in value:
        # East Asian Widthプロパティを取得
        width = unicodedata.east_asian_width(char)
        count += 2 if width in 'FWA' else 1  # F:Fullwidth, W:Wide, A:Ambiguous
    return count

class BlogPageForm(WagtailAdminPageForm):
    def clean_tags(self):
        tags = self.cleaned_data['tags']

        # タグデータの形式変換
        if isinstance(tags, str):
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        elif hasattr(tags, 'all'):
            tag_list = [t.name for t in tags.all()]
        else:
            tag_list = list(tags)

        # 個数制限（4個）
        if len(tag_list) > 4:
            self.add_error('tags', 'タグは最大4個まで選択可能です')

        # 文字数制限
        for tag in tag_list:
            char_count = count_chars(tag)
            if char_count > 10:  # 半角10文字/全角5文字換算
                self.add_error(
                    'tags',
                    f'タグ「{tag}」: 半角10文字/全角5文字以内 (現在 {char_count // 2}全角換算)'
                )

        return tags


# いいねボタンの実装
class Like(models.Model):
    blogpage = models.ForeignKey('BlogPage', verbose_name='ブログ記事', on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blogpage", "ip_address"],
                name="like_unique"
            ),
        ]
# ------いいねボタンここまで


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

class BlogIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)

        # --- パラメータ取得 ---
        tag_param = request.GET.get('tag', '').strip()
        query = request.GET.get('q', '').strip()

        # --- クエリビルド ---
        combined_query = Q()

        # タグ検索（slugベース）
        if tag_param:
            tag_list = tag_param.split()
            tag_query = Q()
            for tag in tag_list:
                tag_query |= Q(tags__slug=tag)
            combined_query &= tag_query
            context['search_tags'] = tag_list
        else:
            context['search_tags'] = []

        # キーワード検索（nameベース：ここではタグ名を検索）
        if query:
            keyword_list = query.split()
            keyword_query = Q()
            for kw in keyword_list:
                keyword_query |= Q(tags__name__icontains=kw)
            combined_query &= keyword_query
            context['search_query'] = query
        else:
            context['search_query'] = ''

        # --- フィルタ & 並び順 ---
        if combined_query:
            blogpages = BlogPage.objects.filter(combined_query).distinct()
        else:
            blogpages = BlogPage.objects.all()

        blogpages = blogpages.live().order_by('-first_published_at')

        # --- ページネーション（12件/ページ） ---
        paginator = Paginator(blogpages, 12)
        page = request.GET.get('page')

        try:
            blogpages_page = paginator.page(page)
        except PageNotAnInteger:
            blogpages_page = paginator.page(1)
        except EmptyPage:
            blogpages_page = paginator.page(paginator.num_pages)

        context['blogpages'] = blogpages_page
        return context

    # 親ページ子ページの制限
    parent_page_types = ['home.HomePage']
    subpage_types = ['blog.BlogPage']

class BlogPage(Page):

    # 親ページ子ページの制御
    parent_page_types = ['blog.BlogIndexPage']
    subpage_types = []
    base_form_class = BlogPageForm

    def clean(self):
        super().clean()

        # タイトル文字数制限
        if len(self.title) > 26:
            raise ValidationError({
                'title': 'タイトルは26文字以内で入力してください'
            })

    # サムネイル
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        related_name='+',
        max_length=1,
        blank=True,
        null=True,
    )

    # 本文
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(
            features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'embed', 'image', 'link', 'document-link', 'code', 'blockquote'],
            blank=True,
            label='テキスト')),
        ('markdown', MarkdownBlock(blank=True, label='マークダウン')),
        ('image', ImageWithCaptionBlock(blank=True, label='画像')),
        ('code', CodeBlock(blank=True, label='コード', default_language='python')),
    ], use_json_field=True)

    # チャンネル
    channel = models.ForeignKey(
        'BlogChannel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # タグ
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('thumbnail', heading='サムネイル'),
            FieldPanel('channel'),
            FieldPanel("tags"),
        ], heading="Blog information"),
        FieldPanel("body", heading='本文'),
    ]

    # いいねボタンの実装

    def get_like_count(self):
        return self.like_set.aggregate(total_likes=models.Sum('count'))['total_likes'] or 0

    def is_liked_by(self, user):
        return self.like_set.filter(user=user).exists()

    # ------いいねボタンここまで
