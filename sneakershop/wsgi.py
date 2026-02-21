"""
WSGI config for sneakershop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# Učitaj .env datoteku iz korijenskog direktorija projekta
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneakershop.settings')

application = get_wsgi_application()
