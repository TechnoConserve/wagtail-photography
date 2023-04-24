import zipfile
from datetime import datetime

import PIL
from django import forms
from django.core.files import File
from wagtail.admin.forms import WagtailAdminModelForm


class AlbumForm(WagtailAdminModelForm):
    zip = forms.FileField(required=False, widget=forms.FileInput(attrs={'accept': '.zip'}))

    def save(self, commit=True):
        album = super().save(commit=False)

        if self.is_valid():
            album.modified = datetime.now()

            if self.cleaned_data['zip'] is not None:
                try:
                    order = album.images.last().sort_order
                except AttributeError:
                    order = 0

                with zipfile.ZipFile(self.cleaned_data['zip']) as archive:
                    for index, entry in enumerate(sorted(archive.namelist())):
                        with archive.open(entry) as file:
                            try:
                                img = album.image_model(name=entry, sort_order=index + order)
                                img.image = File(file)

                                album.images.add(img)

                            except PIL.UnidentifiedImageError:
                                pass

        if commit:
            album.save()

        return album
