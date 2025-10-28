"""
WSGI config for universee project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
# --- Importación Añadida ---
from whitenoise import WhiteNoise
# --- Fin Importación Añadida ---

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'universee.settings')

# --- Línea Modificada ---
# Envuelve la aplicación Django estándar con WhiteNoise
application = WhiteNoise(get_wsgi_application())
# --- Fin Línea Modificada ---