
## Wagtail Photography


Based on [wagtail-photo-gallery](https://github.com/donhauser/wagtail-photo-gallery)

Be warned, I'm mostly using this project as a learning experience for developing and distributing apps. I'm new at it so
things are likely to be broken or break in the future. I use it in production on my own website but would advise against
doing the same if reliability is important to you. I do hope to add tests and generally polish things up in the not so 
distant future.

Wagtail-photography is a Wagtail app to display photographs.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install library

   ```pip install wagtail-photography```

2. Add "wagtail_photography" and wagtail-generic-chooser to your INSTALLED_APPS setting like this:

   ```python
   INSTALLED_APPS = [
      ...
      "wagtail.contrib.modeladmin",
      "wagtail.contrib.routable_page",
      "wagtail_photography",
      "generic_chooser",
   ]
   ```

3. [Setup Wagtail to dynamically serve image urls](https://docs.wagtail.org/en/stable/advanced_topics/images/image_serve_view.html#setup):

   ```python
   from wagtail.images.views.serve import ServeView
   
   urlpatterns = [
       ...
   
       re_path(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$', ServeView.as_view(), name='wagtailimages_serve'),
   
       ...
   
       # Ensure that the wagtailimages_serve line appears above the default Wagtail page serving route
       re_path(r'', include(wagtail_urls)),
   ]
   ```
4. Create a Page model that inherits from `PhotoGalleryMixin`:
   ```python
   class PhotoGallery(PhotoGalleryMixin, Page):
       content = StreamField([
           ("gallery", GalleryBlock()),
       ], blank=True, use_json_field=True)
   
       content_panels = Page.content_panels + [
           FieldPanel("content"),
       ]
   ```
   
5. Run ``python manage.py migrate`` to create the wagtail_photography models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create an album.