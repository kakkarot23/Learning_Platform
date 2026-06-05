"""
WSGI config for oceanix project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oceanix.settings')

application = get_wsgi_application()
