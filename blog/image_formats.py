from django.utils.html import format_html
from wagtail.images.formats import Format, register_image_format, unregister_image_format


class CaptionedImageFormat(Format):

    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)

        return format_html("<figure>{}<figcaption>{}</figcaption></figure>", default_html, alt_text)


class NoCaptionImageFormat(Format):
    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)

        return format_html("<figure>{}</figure>", default_html)


register_image_format(
    CaptionedImageFormat('captioned_image', 'Alt属性をキャプションとして表示する', 'richtext-captioned-image', 'original'),
)
register_image_format(
    NoCaptionImageFormat('no_caption_image', 'キャプションなし', 'richtext-no-caption-image', 'original'),
)

unregister_image_format('fullwidth')
unregister_image_format('left')
unregister_image_format('right')
