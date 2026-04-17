from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),  # for dashboard
    path("chat/", include("chat.urls")),  # for the chat app
    path('rooms/', include('rooms.urls', namespace='rooms')),
]

# Always serve media files — even when DEBUG=False
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
