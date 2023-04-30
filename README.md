=====
Wagtail Photography
=====

Based on [wagtail-photo-gallery](https://github.com/donhauser/wagtail-photo-gallery)

Be warned, this project is still kinda garbage. Mostly I'm just messing about with it but I do hope to polish it up in
the not so distant future.

Wagtail-photography is a Wagtail app to display photographs.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install requirements

   ```pip install wagtail-generic-chooser```


2. Add "wagtail_photography" and wagtail-generic-chooser to your INSTALLED_APPS setting like this:

   ```python
   INSTALLED_APPS = [
      ...
      "generic_chooser"
      "wagtail_photography",
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

3. Run ``python manage.py migrate`` to create the wagtail_photography models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create an album.