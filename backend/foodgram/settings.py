import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-f_eap&w&^7otdz=huwtl3e2#e2ufl%ytrv%1s4o1cx22=b9luu'
)

DEBUG = os.getenv('DJANGO_DEBUG', False) == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1 [::1]').split(' ')

if DEBUG:
    CSRF_TRUSTED_ORIGINS = ['http://*', 'https://*']
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = ['https://foodgram.didns.ru/', 'http://foodgram.didns.ru/']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djoser',
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',
    'api.apps.ApiConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.getenv('DJANGO_ENGINE', 'sqlite3'),
        'NAME': os.getenv('POSTGRES_DB', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.LimitPageNumberPagination',
    'PAGE_SIZE': 6,
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_USER_MODEL = 'users.User'

MAX_PAGE_SIZE = 100
USER_FIRST_NAME_MAX_LENGTH = 150
USER_LAST_NAME_MAX_LENGTH = 150
USER_PASSWORD_MAX_LENGTH = 150
USER_EMAIL_MAX_LENGTH = 254
TAG_NAME_MAX_LENGTH = 200
TAG_SLUG_MAX_LENGTH = 200
TAG_COLOR_MAX_LENGTH = 7
INGREDIENT_NAME_MAX_LENGTH = 200
INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH = 200
RECIPE_NAME_MAX_LENGTH = 200

COOKING_TIME_MIN = 1
INGREDIENT_AMOUNT_MIN = 1
PDF_FONT_SIZE = 12


UNIQUE_TOGETHER_VALIDATOR_DATA = {
    'Subscriptions': {
        'fields': ('user', 'author'),
        'message': 'Вы уже подписаны на этого пользователя.'
    },
    'ShoppingCart': {
        'fields': ('user', 'recipe'),
        'message': 'Этот рецепт уже есть в корзине'
    },
    'FavoriteRecipe': {
        'fields': ('user', 'recipe'),
        'message': 'Этот рецепт уже есть в избранном'
    }
}
