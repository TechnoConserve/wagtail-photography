=====
Wagtail Photography
=====

Based on [wagtail-photo-gallery](https://github.com/donhauser/wagtail-photo-gallery)

Wagtail-photography is a Wagtail app to display photographs.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Install requirements
    
    ```pip install wagtail-generic-chooser```
2. Add "wagtail_photography" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...,
        "wagtail_photography",
    ]

2. Run ``python manage.py migrate`` to create the wagtail_photography models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create an album.