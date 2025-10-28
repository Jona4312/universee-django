"""
Django settings for universee project.
"""

from pathlib import Path
import os # Asegúrate que 'os' esté importado
import dj_database_url

# --- Carga las variables del archivo .env (Necesario para SECRET_KEY, etc.) ---
from dotenv import load_dotenv
load_dotenv()
# --- FIN CARGA .env ---


# =============================
# RUTAS Y CONFIGURACIÓN BASE
# =============================
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================
# SEGURIDAD (AJUSTADO PARA PRODUCCIÓN)
# =============================
# Lee la SECRET_KEY de una variable de entorno (del .env o del sistema)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'un_valor_por_defecto_inseguro_solo_para_desarrollo')

# DEBUG desactivado para producción
DEBUG = False

# Añadido tu host de PythonAnywhere
ALLOWED_HOSTS = ['jonathan4312.pythonanywhere.com']

# =============================
# APLICACIONES INSTALADAS
# =============================
INSTALLED_APPS = [
    # Django por defecto
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Tu app
    "core.apps.CoreConfig",

    # Terceros
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "taggit",
    "whitenoise.runserver_nostatic", # Para WhiteNoise
]

# =============================
# MIDDLEWARE (AJUSTADO PARA WHITENOISE)
# =============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # WhiteNoise Middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# =============================
# URLS Y WSGI
# =============================
ROOT_URLCONF = "universee.urls"
WSGI_APPLICATION = "universee.wsgi.application"

# =============================
# PLANTILLAS
# =============================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

# =============================
# BASE DE DATOS (AJUSTADO PARA PRODUCCIÓN)
# =============================
DATABASES = {
    'default': dj_database_url.config(
        # Lee DATABASE_URL del .env o del sistema. Si no, usa SQLite local.
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# =============================
# VALIDACIÓN DE CONTRASEÑAS
# =============================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================
# INTERNACIONALIZACIÓN
# =============================
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I1N = True
USE_TZ = True

# =============================
# ARCHIVOS ESTÁTICOS & MEDIA (CORRECCIÓN APLICADA AQUÍ)
# =============================
STATIC_URL = "/static/"

# DIRECTORIOS DONDE DJANGO BUSCA ARCHIVOS ESTÁTICOS EN DESARROLLO
# Usamos os.path.join para mayor compatibilidad entre Windows y Linux.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# DONDE SE RECOLECTARÁN LOS ARCHIVOS PARA PRODUCCIÓN
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # WhiteNoise

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================
# AUTENTICACIÓN / ALLAUTH
# =============================
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_RATE_LIMITS = {"login_failed": "5/10m"}
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = None
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# =============================
# CRISPY FORMS (Bootstrap 5)
# =============================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =============================
# CLAVE AUTO-INCREMENTAL
# =============================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================
# EMAIL / SMTP (AJUSTADO PARA PRODUCCIÓN)
# =============================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.pythonanywhere.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587") or 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "UniversoE <no-reply@jonathan4312.pythonanywhere.com>")