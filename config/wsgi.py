"""
WSGI config for config project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Detectar automáticamente el entorno
environment = os.environ.get('ENVIRONMENT', 'development')

if environment == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()