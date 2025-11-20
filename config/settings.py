import os
from pathlib import Path
import dj_database_url

# Carpeta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= CONFIG BÁSICA =================

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-key")

# Podés manejar DEBUG por variable de entorno, por defecto queda encendido
DEBUG = os.environ.get("DEBUG", "1") == "1"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]

# ================= BASE DE DATOS =================
# - Si existe DATABASE_URL → usa Postgres (Render)
# - Si NO existe → usa SQLite local

if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            ssl_require=False,  # si Render exige SSL se puede pasar a True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ================= APPS =================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app_inventario",
]

# ================= MIDDLEWARE =================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

# ================= TEMPLATES =================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ================= ESTÁTICOS =================

STATIC_URL = "/static/"
# Si en algún momento querés colectar estáticos para producción:
# STATIC_ROOT = BASE_DIR / "staticfiles"
