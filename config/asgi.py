import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

import chat.routing

# Create the base Django ASGI app
django_asgi_app = get_asgi_application()

# Wrap it with WhiteNoise so it can serve /static/ and /media/
django_asgi_app = WhiteNoise(
    django_asgi_app,
    root=os.getenv("MEDIA_ROOT")  # Serve media files
)

# Explicitly add the media directory
django_asgi_app.add_files(os.getenv("MEDIA_ROOT"), prefix="media/")

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
