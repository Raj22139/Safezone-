from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/crime-feed/$',     consumers.CrimeFeedConsumer.as_asgi()),
    re_path(r'ws/safety-alerts/$',  consumers.SafetyAlertConsumer.as_asgi()),
]
