import os

from django.core.asgi import get_asgi_application
from examiner.settings import BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examiner.settings')

application = get_asgi_application()
