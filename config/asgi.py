import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from whitenoise import WhiteNoise
from django.conf import settings  # <-- IMPORTANT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

import chat.routing

# Base Django ASGI app
django_asgi_app = get_asgi_application()

# Wrap with WhiteNoise to serve static + media
django_asgi_app = WhiteNoise(
    django_asgi_app,
    root=settings.STATIC_ROOT  # static files
)

# Add MEDIA files explicitly
django_asgi_app.add_files(settings.MEDIA_ROOT, prefix="media/")

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
