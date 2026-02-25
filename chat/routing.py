from django.urls import re_path
from . import consumers

# shortuuid generates IDs with hyphens 
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[\w-]+)/$', consumers.chatconsumer.as_asgi()),
]