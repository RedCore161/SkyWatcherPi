"""
WSGI config for SkyWatcherCC project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SkyWatcherCC.settings")

application = get_wsgi_application()
