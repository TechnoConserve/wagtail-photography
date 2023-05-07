from django.utils.functional import cached_property
from wagtail import blocks
from wagtail.coreutils import resolve_model_string

from .widgets import CollectionChooser


class CollectionChooserBlock(blocks.ChooserBlock):
    class Meta:
        icon = 'folder'

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    @property
    def target_model(self):
        return resolve_model_string('wagtailcore.Collection')

    @cached_property
    def widget(self):
        return CollectionChooser()


class GalleryBlock(blocks.StructBlock):
    album_class = 'wagtail_photography.Album'

    title = blocks.CharBlock()
    collection = CollectionChooserBlock()

    class Meta:
        template = 'wagtail_photography/blocks/photo_gallery.html'
        icon = 'image'

    @property
    def target_model(self):
        return resolve_model_string(self.album_class)

    def filter_albums(self, value):
        collection = value['collection']
        query_set = collection.get_descendants(True)

        return self.target_model.objects.filter(collection__in=query_set, is_visible=True)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['albums'] = self.filter_albums(context['self']).order_by('-created')
        context['detail_url'] = 'album/'

        return context
