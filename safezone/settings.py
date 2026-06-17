"""
SafeZone AI — Django Settings
AI-Based Crime and Area Safety Intelligence System
"""

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ════════════════════════════════════════
# SECURITY
# ════════════════════════════════════════
SECRET_KEY   = config('SECRET_KEY', default='django-insecure-change-this-in-production-xyz123')
DEBUG        = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,safezone-6.onrender.com'
).split(',')

# ════════════════════════════════════════
# INSTALLED APPS
# ════════════════════════════════════════
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',

    # MTech Advanced Features
    'rest_framework',
    'drf_yasg',
    'channels',
    # Local apps
    'accounts',
    'crime',
    'dashboard',
    'admin_panel',
    'ml',
    'chatbot',
]

# ════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF      = 'safezone.urls'
WSGI_APPLICATION  = 'safezone.wsgi.application'

# ════════════════════════════════════════
# TEMPLATES
# ════════════════════════════════════════
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# print("DB_PASSWORD =", config('DB_PASSWORD', default='NOT_FOUND'))
# ════════════════════════════════════════
# DATABASE — PostgreSQL
# ════════════════════════════════════════
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME',     default='safezone_db'),
        'USER':     config('DB_USER',     default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='12345'),
        'HOST':     config('DB_HOST',     default='localhost'),
        'PORT':     config('DB_PORT',     default='5432'),
    }
}

# ════════════════════════════════════════
# AUTH & PASSWORD VALIDATION
# ════════════════════════════════════════
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ════════════════════════════════════════
# INTERNATIONALIZATION
# ════════════════════════════════════════
LANGUAGE_CODE       = 'en-us'
TIME_ZONE           = 'Asia/Kolkata'
USE_I18N            = True
USE_TZ              = True
LANGUAGE_COOKIE_NAME= 'safezone_language'

# ════════════════════════════════════════
# STATIC & MEDIA FILES
# ════════════════════════════════════════
STATIC_URL      = '/static/'
STATIC_ROOT     = BASE_DIR / 'staticfiles'
STATICFILES_DIRS= [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ════════════════════════════════════════
# CRISPY FORMS
# ════════════════════════════════════════
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

# ════════════════════════════════════════
# SESSION
# ════════════════════════════════════════
SESSION_COOKIE_AGE         = 86400   # 1 day
SESSION_SAVE_EVERY_REQUEST = True

# ════════════════════════════════════════
# EMAIL — Gmail SMTP
# ════════════════════════════════════════
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = config('EMAIL_HOST',          default='smtp.gmail.com')
EMAIL_PORT          = config('EMAIL_PORT',          default=587, cast=int)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS       = config('EMAIL_USE_TLS',       default=True, cast=bool)
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER

# ════════════════════════════════════════
# ML MODEL
# ════════════════════════════════════════
ML_MODEL_PATH = BASE_DIR / 'ml' / 'trained_model' / 'risk_model.pkl'

# ════════════════════════════════════════
# CHATBOT — Anthropic Claude API (optional)
# Get key from: https://console.anthropic.com/
# ════════════════════════════════════════
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')

# ════════════════════════════════════════
# GOOGLE MAPS — Route Safety Checker (optional)
# Get key from: https://console.cloud.google.com/
# ════════════════════════════════════════
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# ════════════════════════════════════════
# WHATSAPP ALERTS (optional)
# ════════════════════════════════════════
WHATSAPP_API_URL   = config('WHATSAPP_API_URL',   default='')
WHATSAPP_API_TOKEN = config('WHATSAPP_API_TOKEN', default='')

# ════════════════════════════════════════
# PWA — Progressive Web App
# ════════════════════════════════════════
PWA_APP_NAME            = 'SafeZone AI'
PWA_APP_DESCRIPTION     = 'AI-Based Crime and Area Safety Intelligence System'
PWA_APP_THEME_COLOR     = '#1A56FF'
PWA_APP_BACKGROUND_COLOR= '#F0F2F8'


# ════════════════════════════════════════
# DJANGO REST FRAMEWORK
# ════════════════════════════════════════
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    }
}

# ════════════════════════════════════════
# DJANGO CHANNELS (WebSocket)
# ════════════════════════════════════════
ASGI_APPLICATION = 'safezone.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # For production use Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    }
}

# ════════════════════════════════════════
# 2FA — Two Factor Authentication
# ════════════════════════════════════════
TWO_FACTOR_ENABLED = True
OTP_TOTP_ISSUER = 'SafeZone AI'

# ════════════════════════════════════════
# TELEGRAM BOT (optional)
# ════════════════════════════════════════
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')

# ════════════════════════════════════════
# API RATE LIMITING
# ════════════════════════════════════════
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
