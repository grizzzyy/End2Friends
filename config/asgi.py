import os
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "End2Friends.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": ... (you will add this later when you create messaging)
})
