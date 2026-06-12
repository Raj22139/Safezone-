"""
SafeZone AI — Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django built-in admin (separate from our custom admin panel)
    path('django-admin/', admin.site.urls),

    # Main website (landing page, about, etc.)
    path('', include('crime.urls')),

    # User authentication
    path('accounts/', include('accounts.urls')),

    # User dashboard
    path('dashboard/', include('dashboard.urls')),

    # Custom admin panel
    path('admin-panel/', include('admin_panel.urls')),

    # Chatbot API
    path('chatbot/', include('chatbot.urls')),

    # REST API + Swagger
    path('api/', include('api.urls')),

    # WebSocket (via ASGI — no URL needed here, handled by routing.py)


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error pages
handler404 = 'crime.views.error_404'
handler500 = 'crime.views.error_500'
