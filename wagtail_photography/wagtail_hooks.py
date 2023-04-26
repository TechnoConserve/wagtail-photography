from wagtail.core import hooks

from wagtail_photography.views import CollectionChooserViewSet


@hooks.register('register_admin_viewset')
def register_collection_chooser_viewset():
    return CollectionChooserViewSet('collection_chooser', url_prefix='collection-chooser')
