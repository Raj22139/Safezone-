"""
SafeZone AI — REST API URLs
Swagger UI: /api/docs/
ReDoc:       /api/redoc/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from . import views

# Swagger schema config
schema_view = get_schema_view(
    openapi.Info(
        title           = 'SafeZone AI REST API',
        default_version = 'v1',
        description     = '''
## SafeZone AI — Crime & Area Safety Intelligence API

AI-powered REST API for crime data analysis and area safety scoring.

### Features
- 🔍 **Area Safety Search** — Query any location, get AI risk score
- 📊 **Crime Records** — Full CRUD for crime incidents
- 🗺️ **Area Management** — List/filter/analyze areas
- 📈 **Analytics** — City stats, crime distribution, trends
- 🕐 **Search History** — User-specific search logs

### Authentication
Use session auth or token auth:
```
Authorization: Token your-token-here
```

### Rate Limits
- Anonymous: 100 requests/day
- Authenticated: 1000 requests/day
        ''',
        contact = openapi.Contact(email='admin@safezone.ai'),
        license = openapi.License(name='MIT License'),
    ),
    public      = True,
    permission_classes = [AllowAny],
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'areas',        views.AreaViewSet,        basename='area')
router.register(r'crime-records',views.CrimeRecordViewSet, basename='crime-record')

app_name = 'api'

urlpatterns = [
    # Swagger UI + ReDoc
    path('docs/',  schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',   cache_timeout=0), name='redoc'),
    path('schema/',schema_view.without_ui(cache_timeout=0),         name='schema-json'),

    # Token Auth
    path('auth/token/', token_views.obtain_auth_token, name='api-token'),

    # ViewSet routes
    path('v1/', include(router.urls)),

    # Custom endpoints
    path('v1/search/',    views.AreaSearchAPIView.as_view(),  name='search'),
    path('v1/analytics/', views.AnalyticsAPIView.as_view(),   name='analytics'),
    path('v1/history/',   views.UserHistoryAPIView.as_view(), name='history'),
]
