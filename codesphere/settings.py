"""
Configuración principal de CodeSphere.
Autenticación tradicional y acceso con Google OAuth.
"""

import os
from pathlib import Path


# ============================================================
# RUTAS Y CONFIGURACIÓN GENERAL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-solo-para-desarrollo-local"
)

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://codeshpere.onrender.com",
]


# ============================================================
# APLICACIONES
# ============================================================

INSTALLED_APPS = [
    # Aplicaciones internas de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Autenticación con django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Aplicación principal
    "social.apps.SocialConfig",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    # Necesario para django-allauth
    "allauth.account.middleware.AccountMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# RUTAS PRINCIPALES
# ============================================================

ROOT_URLCONF = "codesphere.urls"

WSGI_APPLICATION = "codesphere.wsgi.application"


# ============================================================
# PLANTILLAS HTML
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# BASE DE DATOS
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# AUTENTICACIÓN
# ============================================================

AUTHENTICATION_BACKENDS = [
    # Mantiene el inicio de sesión tradicional de Django
    "django.contrib.auth.backends.ModelBackend",

    # Añade autenticación mediante proveedores externos
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Evita iniciar el flujo OAuth mediante una petición GET.
SOCIALACCOUNT_LOGIN_ON_GET = False


# ============================================================
# GOOGLE OAUTH
# ============================================================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

SOCIALACCOUNT_PROVIDERS = {}

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "APPS": [
                {
                    "client_id": GOOGLE_CLIENT_ID,
                    "secret": GOOGLE_CLIENT_SECRET,
                    "key": "",
                }
            ],
            "SCOPE": [
                "profile",
                "email",
            ],
        }
    }

SOCIALACCOUNT_LOGIN_ON_GET = True
# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# IDIOMA Y ZONA HORARIA
# ============================================================

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True
USE_TZ = True


# ============================================================
# ARCHIVOS ESTÁTICOS
# ============================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# SEGURIDAD HTTP Y COOKIES
# ============================================================

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# ============================================================
# CONFIGURACIÓN DE MODELOS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
