from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# === Flags desde entorno (local por defecto) ===
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

# Hosts permitidos
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# Si Render expone la URL pública, la añadimos (host y CSRF)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    p = urlparse(RENDER_EXTERNAL_URL)
    if p.hostname and p.hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(p.hostname)
    CSRF_TRUSTED_ORIGINS = [f"{p.scheme}://{p.hostname}"]
else:
    CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1", "http://localhost"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # sirve estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'puntosapp.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # carpeta /templates en la raíz
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = 'puntosapp.wsgi.application'

# === Base de datos: Postgres en Render (DATABASE_URL), SQLite en local ===
if os.getenv("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv("DATABASE_URL"), conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# === Estáticos ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']      # tu logo/css/js están en /static (raíz)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Render/Proxy HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
