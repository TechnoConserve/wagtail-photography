from django.utils.translation import gettext_lazy as _
from generic_chooser.views import ModelChooserViewSet
from wagtail.models import Collection


class CollectionChooserViewSet(ModelChooserViewSet):
    icon = 'folder'
    model = Collection
    page_title = _('Choose a collection')
    per_page = 10
