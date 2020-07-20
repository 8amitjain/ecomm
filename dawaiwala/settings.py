import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20gn)u#^n#menvc&*4!=_quw-9#zneh_213z_cxa8r^0$p9-!m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # 'home.apps.HomeConfig',
    'users.apps.UsersConfig',
    'store.apps.StoreConfig',
    'vendors.apps.VendorsConfig',
    'crispy_forms',
    'django_filters',
    'django_countries',
    'widget_tweaks',
    'mapwidgets',
    "django.contrib.gis",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "ecomm",
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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

GOOGLE_MAP_API_KEY = "AIzaSyBwRaz6Qcmyquj2GG5g4RChfBecOg641Qg"

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocation", [21.0064725, 75.5553983]),
        ("markerFitZoom", 11),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'uk'}})
    ),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAP_API_KEY,
}


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
EMAIL_HOST_USER = 'visionboard.help@gmail.com'
EMAIL_HOST_PASSWORD = 'edqvopggdzwivnlk'
# os.environ.get('EMAIL_HOST_USER')

STRIPE_PUBLISHABLE_KEY = 'pk_test_51GziiaEMM8ICDJpWkzDBSC4IRrZZiae23SdzYedj0uPaKdSYwf6jJui0VfF2RFgMa1looBaTq82qRrvsLe0wkFqm00llm82WLu'
STRIPE_SECRET_KEY = 'sk_test_51GziiaEMM8ICDJpWgnWlUH3cBzh6IOrYqTPpB7SgD5ZCZWb4sHcoa6WWd5BU69IhngDN0igApImzgA9aiZZj9k0y006rsHOJiB'

