"""
Django settings for universee project.
"""

from pathlib import Path
import os
import dj_database_url # <--- Importado para la base de datos

# =============================
# RUTAS Y CONFIGURACIÓN BASE
# =============================
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================
# SEGURIDAD (AJUSTADO PARA PRODUCCIÓN)
# =============================
# --- ¡CAMBIO! Lee la SECRET_KEY de una variable de entorno ---
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'un_valor_por_defecto_inseguro_solo_para_desarrollo')
# --- FIN CAMBIO ---

# --- ¡CAMBIO! DEBUG desactivado para producción ---
DEBUG = False
# --- FIN CAMBIO ---

# --- ¡CAMBIO! Añadido tu host de PythonAnywhere ---
# Si usas un dominio propio en el futuro, añádelo a esta lista
ALLOWED_HOSTS = ['jonathan4312.pythonanywhere.com']
# --- FIN CAMBIO ---

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
    "whitenoise.runserver_nostatic", # <-- Añadido para WhiteNoise
]

# =============================
# MIDDLEWARE (AJUSTADO PARA WHITENOISE)
# =============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # --- ¡CAMBIO! Añadido WhiteNoise Middleware ---
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # --- FIN CAMBIO ---
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware", # Considera moverlo después de Session y Auth si usas mensajes de allauth
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
# --- ¡CAMBIO! Usamos dj_database_url para leer la config de una variable de entorno ---
DATABASES = {
    'default': dj_database_url.config(
        # Intenta obtener la URL de la variable de entorno DATABASE_URL
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', # Si no existe, usa SQLite (para desarrollo local)
        conn_max_age=600 # Opcional: mantiene las conexiones abiertas por 10 minutos
    )
}
# --- FIN CAMBIO ---


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
# ARCHIVOS ESTÁTICOS & MEDIA (AJUSTADO PARA WHITENOISE)
# =============================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles" # Django colectará aquí los estáticos para producción

# --- ¡CAMBIO! Configuración de WhiteNoise ---
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# --- FIN CAMBIO ---

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

# (Tu configuración de Allauth se mantiene igual)
ACCOUNT_LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_RATE_LIMITS = {"login_failed": "5/10m"}
ACCOUNT_EMAIL_VERIFICATION = "none" # <-- Mantenido en none por simplicidad inicial
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

# --- ¡CAMBIO! Usamos el backend SMTP estándar ---
# PythonAnywhere interceptará esto si no configuras las variables,
# usando su propio servidor para cuentas gratuitas.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# --- FIN CAMBIO ---

# Leemos la configuración desde variables de entorno
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.pythonanywhere.com") # Default para PA si no usas otro
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587") or 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "") # Tu usuario de PA o del servicio de email
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "") # Tu contraseña
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "UniversoE <no-reply@jonathan4312.pythonanywhere.com>") # Email desde el que se envían

# (Otras configuraciones que puedas tener...)