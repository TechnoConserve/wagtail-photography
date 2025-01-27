import copy
import itertools
import uuid

from django.db import models
from django.http import Http404
from django.shortcuts import render
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel, TabbedInterface, ObjectList, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.coreutils import resolve_model_string
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.views.serve import generate_image_url
from wagtail.models import Orderable

from .blocks import GalleryBlock
from .forms import AlbumForm


class Album(ClusterableModel):
    base_form_class = AlbumForm
    image_class = 'wagtail_photography.AlbumImage'

    collection = models.ForeignKey(
        'wagtailcore.Collection',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    title = models.CharField(max_length=70)
    description = models.TextField(max_length=1024)

    cover = models.OneToOneField(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_for',
    )

    is_visible = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=50, unique=True)

    @property
    def image_model(self):
        return resolve_model_string(self.image_class)

    panels = [
        FieldPanel('title'),
        FieldPanel('collection'),
        FieldPanel('description'),
        FieldPanel('zip', heading='Upload a .zip file'),
        MultiFieldPanel([
            HelpPanel('<h2>How to sort and delete images</h2>' +
                      'Drag-and-drop to change the position of an image.<br />' +
                      'Hold down the right mouse button when hovering over an image to enter selection mode.<br />' +
                      'Right-click an image to open a context menu.<br />' +
                      'You may use the middle mouse button to drag around multiple selected images.'),
            InlinePanel('images'),
        ], heading='Album Images'),
        FieldPanel('cover')
    ]

    settings_panel = [
        FieldPanel('slug'),
        FieldPanel('is_visible'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading='Content'),
        ObjectList(settings_panel, heading='Settings'),
    ])

    def __str__(self):
        return self.title


class AlbumImage(Orderable):
    name = models.CharField(max_length=255, default=None, null=True)
    image = models.ForeignKey('wagtailimages.Image', on_delete=models.SET_NULL, null=True)
    album = ParentalKey('Album', on_delete=models.CASCADE, related_name='images')
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=70, default=uuid.uuid4, editable=False)

    panels = [
        FieldPanel('image'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._original_image = copy.copy(self.image)

    def __str__(self):
        return self.name or str(super())

    @property
    def alt(self):
        return "Album Image"


class PhotoGalleryMixin(RoutablePageMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get a list of all StreamFields defined in this class
        # The getattr() is required to get concrete iterable instances
        self._stream_fields = [getattr(self, f.name) for f in self._meta.get_fields() if isinstance(f, StreamField)]

        # Filter out GalleryBlocks from each StreamField
        self._gallery_blocks = [filter(lambda x: isinstance(x.block, GalleryBlock), f) for f in self._stream_fields]
        # Flatten the result into a single list of GalleryBlocks
        self._gallery_blocks = list(itertools.chain(*self._gallery_blocks))

    @route(r'^album/(.+)/$')
    def serve_album(self, request, slug):

        # search for the album slug in all gallery blogs
        for gallery in self._gallery_blocks:
            try:
                album = gallery.block.filter_albums(gallery.value).get(slug=slug)

            except Album.DoesNotExist:
                continue

            image_data = []
            for album_image in album.images.all():
                image = album_image.image
                image_data.append({'image': image,
                                   'jpeg_image_url': generate_image_url(image, 'fill-300x300|format-jpeg'),
                                   'webp_image_url': generate_image_url(image, 'fill-300x300|format-webp'),
                                   'album_image': album_image,
                                   })

            return render(
                request,
                'wagtail_photography/album_detail.html',
                {'page': self, 'album': album, 'image_data': image_data}
            )

        raise Http404
