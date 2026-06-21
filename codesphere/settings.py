"""
Django settings for codesphere project (PRODUCCIÓN SEGURA)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# 🔐 SEGURIDAD
# =========================

# SECRET KEY desde variables de entorno (IMPORTANTE)
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-only-dev")

# DEBUG SIEMPRE OFF en producción
DEBUG = False

# Dominios permitidos (Railway + local)
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".railway.app",
]


# =========================
# APPS
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # tu app
    'social.apps.SocialConfig',
]


# =========================
# MIDDLEWARE (SEGURIDAD)
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 importante para Railway

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'codesphere.urls'


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'codesphere.wsgi.application'


# =========================
# BASE DE DATOS
# =========================
# (puedes dejar SQLite para empezar)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# PASSWORDS SEGURAS
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# INTERNACIONALIZACIÓN
# =========================

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES (RAILWAY)
# =========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =========================
# MEDIA (IMÁGENES / POSTS)
# =========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# LOGIN SYSTEM
# =========================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'


# =========================
# SEGURIDAD EXTRA (PRODUCCIÓN)
# =========================

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# SOLO activar si usas HTTPS (Railway lo usa)
SECURE_SSL_REDIRECT = True