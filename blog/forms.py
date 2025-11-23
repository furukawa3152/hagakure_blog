from django.core.exceptions import ValidationError
from wagtail.admin.forms import WagtailAdminPageForm

from .models import BlogPage


def count_chars(value: str) -> int:
    """半角文字を1、全角文字を2としてカウント（tests.BlogPageFormTests で検証）"""
    import unicodedata

    count = 0
    for char in value:
        width = unicodedata.east_asian_width(char)
        count += 2 if width in 'FWA' else 1  # F:Fullwidth, W:Wide, A:Ambiguous
    return count


class BlogPageForm(WagtailAdminPageForm):
    """BlogPageのタグ制約を司るフォーム（tests.BlogPageFormTests で検証）"""

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
