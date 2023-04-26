import copy
import itertools
import uuid

from django import forms
from django.db import models
from django.http import Http404
from django.shortcuts import render
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel, TabbedInterface, ObjectList, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.coreutils import resolve_model_string
from wagtail.fields import StreamField
from wagtail.models import Orderable

from .blocks import GalleryBlock
from .forms import AlbumForm
from .widgets import PictureWidget

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
        'wagtail_photography.AlbumImage',
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
        FieldPanel('cover', widget=forms.widgets.Input, classname='hidden_field')
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
    image = ProcessedImageField(upload_to='albums', processors=[ResizeToFit(1920, 1920)], format='JPEG',
                                options={'quality': 80})
    thumb = ProcessedImageField(upload_to='albums', processors=[ResizeToFit(300, 300)], format='JPEG', options={'quality': 80}, blank=True)
    album = ParentalKey('Album', on_delete=models.CASCADE, related_name='images')
    created = models.DateTimeField(auto_now_add=True)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    slug = models.SlugField(max_length=70, default=uuid.uuid4, editable=False)

    panels = [
        FieldPanel('thumb', widget=PictureWidget),
        FieldPanel('image'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._original_image = copy.copy(self.image)

    @property
    def alt(self):
        return "Album Image"

    def __str__(self):
        return self.name or str(super())


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

            return render(
                request,
                'wagtail_photography/album_detail.html',
                {'page': self, 'album': album, 'images': album.images.all()}
            )

        raise Http404