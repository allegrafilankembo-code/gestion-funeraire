import os
from pathlib import Path
import dj_database_url

# 1. Chemins de base (BASE_DIR)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Sécurité de base
# Lit la clé secrète depuis Render en production, ou utilise la clé locale du fichier .env
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-locale-dev-key-change-me')

# DEBUG est True en local, mais DOIT être False sur Render
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Domaines autorisés à faire tourner l'application
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.render.com', # Permet à Render d'accéder à l'application
]

# 3. Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # REQUIS pour collectstatic
    
    # Vos applications tierces présentes dans vos requirements
    'corsheaders',
    'django_filters',
    'leaflet',
    'ninja_extra',
    
    # Ajoutez ici vos propres applications locales Django (ex: 'cimetiere_app')
]

# 4. Middlewares (L'ordre est très important, notamment pour Whitenoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Gère les fichiers CSS/JS sur Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Gère la sécurité des requêtes API
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration de la racine de votre projet
ROOT_URLCONF = 'cimetiere.urls'

# 5. Gestion des templates HTML
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

WSGI_APPLICATION = 'cimetiere.wsgi:application'

# 6. Base de données (SQLite en local / PostgreSQL automatique sur Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# 7. Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. Internationalisation (Langue et Heure)
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 9. Fichiers Statiques (CSS, JS, Images) - ESSENTIEL pour Render
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Permet à Whitenoise de compresser et mettre en cache les fichiers statiques pour être ultra rapide
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# 10. Type de clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 11. Sécurité CORS (Optionnel mais recommandé pour Django Ninja)
CORS_ALLOW_ALL_ORIGINS = DEBUG # Autorise tout le monde en local, bloque en production
