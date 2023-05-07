from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from wagtail_photography.blocks import GalleryBlock
from wagtail_photography.models import PhotoGalleryMixin


class HomePage(Page):
    pass


class GalleryPage(PhotoGalleryMixin, Page):
    content = StreamField([
        ("gallery", GalleryBlock()),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]


