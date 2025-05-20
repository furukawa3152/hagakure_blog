from wagtail import blocks
from wagtail.blocks import CharBlock
from wagtail.images.blocks import ImageChooserBlock


class ImageWithCaptionBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label='画像')
    caption = CharBlock(required=False, label='キャプション')

    class Meta:
        template = 'blocks/image_with_caption.html'
        icon = 'image'
