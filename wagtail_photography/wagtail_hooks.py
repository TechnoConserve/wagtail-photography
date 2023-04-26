from django.utils.html import format_html
from django.templatetags.static import static
from wagtail.core import hooks

from wagtail_photography.views import CollectionChooserViewSet


@hooks.register("insert_global_admin_css", order=100)
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("photo_gallery_admin.css")
    )


@hooks.register("insert_global_admin_js", order=100)
def global_admin_js():
    return format_html(
        '<script src="{}"></script>',
        static("photo_gallery_admin.js")
    )


@hooks.register('register_admin_viewset')
def register_collection_chooser_viewset():
    return CollectionChooserViewSet('collection_chooser', url_prefix='collection-chooser')
