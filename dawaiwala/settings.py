import os
from .data import  Secret_key, Email, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, GOOGLE_MAP_API_KEY
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from pprint import pprint

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = Secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # 'home.apps.HomeConfig',
    'users.apps.UsersConfig',
    'store.apps.StoreConfig',
    'vendors.apps.VendorsConfig',
    'rest_api.apps.RestApiConfig',
    'frontend.apps.FrontendConfig',
    'crispy_forms',
    'django_filters',
    'django_countries',
    'widget_tweaks',
    'mapwidgets',
    'rest_framework',
    'knox',
    'django_rest_passwordreset',

    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dawaiwala.urls'

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

WSGI_APPLICATION = 'dawaiwala.wsgi.application'


# Database

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
#     }
# }


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "dawaiwala",
        "USER": "postgres",
        "PASSWORD": "amitjain",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

GDAL_LIBRARY_PATH = r'E:\Coding\Python\django\Dawaiwala-online\venv\Lib\site-packages\osgeo\gdal301.dll'

PROJ_DIR = r'E:\Coding\Python\django\Dawaiwala-online\venv\Lib\site-packages\osgeo\data\proj'


STATIC_URL = '/static/'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = 'store:store'
LOGIN_URL = 'users-login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = Email
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# os.environ.get('EMAIL_HOST_USER')

GOOGLE_MAP_API_KEY = GOOGLE_MAP_API_KEY

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocation", [21.0064725, 75.5553983]),
        ("markerFitZoom", 11),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'uk'}})
    ),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAP_API_KEY,
}
STRIPE_PUBLISHABLE_KEY = STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY = STRIPE_SECRET_KEY

