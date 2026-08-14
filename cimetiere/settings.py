import os
from pathlib import Path
import dj_database_url  # Utile pour la base de données Render

# 1. Définir BASE_DIR EN PREMIER
BASE_DIR = Path(__file__).resolve().parent.parent

# ... (laissez vos autres configurations comme SECRET_KEY, DEBUG, etc.)

# 2. Remplacer votre bloc DATABASES par celui-ci (compatible local et Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si Render fournit une base de données PostgreSQL, Django l'utilisera automatiquement
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
