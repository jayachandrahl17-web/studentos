"""
WSGI configuration for the StudyOS Django backend.

WSGI is the interface that allows a web server to run our Django application.
For local development, Django's runserver uses this file too.
"""

import os

from django.core.wsgi import get_wsgi_application


# Tell Django which settings file to use.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# This is the application Django expects.
application = get_wsgi_application()
