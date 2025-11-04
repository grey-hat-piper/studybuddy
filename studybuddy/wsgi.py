"""
WSGI config for studybuddy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# import os
# import sys

# # ensure your project root is on path if necessary
# ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # adjust if needed
# sys.path.append(ROOT_DIR)

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybuddy.settings')

# application = get_wsgi_application()

# app = application

import os, sys

# Check what Python can see
print("=== Vercel debug start ===")
print("Current working dir:", os.getcwd())
print("Sys.path:", sys.path)
print("Env vars keys:", list(os.environ.keys()))
print("=== Vercel debug end ===")

# Make sure Django settings is set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studybuddymanager.settings")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
except Exception as e:
    print("WSGI initialization failed:", e)
    raise
