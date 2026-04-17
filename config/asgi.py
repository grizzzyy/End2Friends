import os
import django
from django.core.asgi import get_asgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing


class MediaFileMiddleware:
    """Serve /media/ files without interfering with WebSockets."""
    def __init__(self, app):
        self.app = app
        self.media_url = settings.MEDIA_URL
        self.media_root = str(settings.MEDIA_ROOT)

    async def __call__(self, scope, receive, send):
        # Only intercept HTTP requests
        if scope["type"] == "http" and scope["path"].startswith(self.media_url):
            await self._serve_media(scope, receive, send)
        else:
            # Pass WebSocket scopes straight through
            await self.app(scope, receive, send)

    async def _serve_media(self, scope, receive, send):
        import mimetypes, aiofiles, os
        from urllib.parse import unquote

        relative = unquote(scope["path"][len(self.media_url):])
        full_path = os.path.realpath(os.path.join(self.media_root, relative))

        if not full_path.startswith(os.path.realpath(self.media_root)) or not os.path.isfile(full_path):
            await self._send_404(send)
            return

        content_type, _ = mimetypes.guess_type(full_path)
        content_type = content_type or "application/octet-stream"
        file_size = os.path.getsize(full_path)

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", content_type.encode()),
                (b"content-length", str(file_size).encode()),
            ],
        })

        async with aiofiles.open(full_path, "rb") as f:
            while chunk := await f.read(65536):
                await send({
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                })

        await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def _send_404(self, send):
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-type", b"text/plain")],
        })
        await send({"type": "http.response.body", "body": b"Not Found"})


# Django ASGI app
django_asgi_app = get_asgi_application()

# Wrap ONLY the HTTP app
http_app = MediaFileMiddleware(django_asgi_app)

# Final ASGI application
application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
