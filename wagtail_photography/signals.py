import io
import uuid

from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from pilkit.processors import ResizeToFit
from wagtail_photography.models import AlbumImage


@receiver(pre_save, sender=AlbumImage)
def preprocess_for_db(sender, **kwargs):
    # Ignore unchanged images
    if sender._original_image == sender.image:
        return

    if not sender.name:
        sender.name = sender.image.name

    with Image.open(sender.image) as image:
        processor = ResizeToFit(1920, 1920)
        image = processor.process(image)

        image = image.convert("RBG")

        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=80)

        contentfile = ContentFile(img_bytes.getvalue())

        sender.width, sender.height = image.size

        filename = uuid.uuid4().hex

        sender.image.save(filename, contentfile, save=False)
        #sender.thumb.save(f'thumb-{filename}', contentfile, save=False)
