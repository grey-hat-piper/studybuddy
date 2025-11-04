"""
WSGI config for studybuddy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# api/wsgi.py
import os
import sys

# ensure your project root is on path if necessary
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # adjust if needed
sys.path.append(ROOT_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybuddy.settings')

application = get_wsgi_application()

app = application