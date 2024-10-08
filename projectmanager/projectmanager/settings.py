"""
Django settings for projectmanager project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+49#s-ax0#@7y8!xh&nc*g5=9+r7&&ks-9c0wwadb=bp!j-1y$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    'https://dev.entv.events/',
    'https://frame-dev-test.frame-dev.com',
    'https://652f-2403-6200-8831-1d34-51f8-29ed-3d47-4184.ngrok-free.app',
    'https://liff.line.me/',
]
# Application definition

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    #packages
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.line',
    'crispy_forms',
    'crispy_bootstrap5',
    'crispy_tailwind',
    'ckeditor',
    'django_htmx',
    'mapbox_location_field',
    'django_filters',
    # App
    'activity',
    'base',
]


# CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

# CRISPY_TEMPLATE_PACK = "tailwind"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'projectmanager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path.joinpath(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'activity.context_processors.user_organizer',
            ],
        'libraries':{
                'date_th': 'activity.templatetags.date_th',
                'attendance_filters': 'activity.templatetags.attendance_filters'
            }
        },
    },
]

WSGI_APPLICATION = 'projectmanager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'timezone': 'Asia/Bangkok',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bangkok'

# USE_I18N = True

USE_TZ = True


SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [Path.joinpath(BASE_DIR, 'static')]
STATIC_ROOT = Path.joinpath(BASE_DIR, 'staticfiles')

# STATIC_URL = 'staticfiles/'

# STATICFILES_DIRS = [Path.joinpath(BASE_DIR, 'static')]
# STATIC_ROOT = Path.joinpath(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # ปรับเส้นทางตามต้องการ

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# allauth
ACCOUNT_ADAPTER = 'base.adapter.MyAccountAdapter'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_LOGIN_ON_GET=True
LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'line': {
            'APP': {
                  'client_id': '2006304809',
                  'secret': '2ad755bcdce337aa003e625ea886159e'
            },
            "SCOPE": ['profile', 'openid', 'email']
    },
}

# CKEDITOR
CKEDITOR_BASEPATH = "/static/ckeditor/"
CKEDITOR_UPLOAD_PATH = "ckeditor/"
X_FRAME_OPTIONS = 'SAMEORIGIN'
CKEDITOR_CONFIGS = {
    'default': {
        # 'allowedContent': True,
        'toolbar': 'full',
        'width': '100%',
        'height': '500px',
        # 'extraAllowedContent': '*',
        'extraPlugins': ','.join(
            [
                'youtube',
                'codesnippet',
            ]
        ),
    },
}

# LINE Messaging API
channel_access_token = 'f45bC3kWUn7IkGi6HKTqQ+5estYC0uhyz4t+YBSQ3ABJRzoQg9V2FUkQkgFWLzdXld4SK1DQExeC78nf+vzQTal4xSSAORFAk0/64i600YaN1iPTqNTNUrWyTWuOzxFuOt96tAi3Q3CmUZ0WxHm4kwdB04t89/1O/w1cDnyilFU='
channel_secret = 'deaddb80853cf5a78fb2ae159fddba5b'

domain_media = 'https://frame-dev-test.frame-dev.com/media'
# domain_media = 'https://dev.entv.events/media'
domain_liff = 'https://liff.line.me/2006304809-k4W7Wdro'
domain = 'https://652f-2403-6200-8831-1d34-51f8-29ed-3d47-4184.ngrok-free.app'

# MAPBOX
if os.name == 'nt':
    VIRTUAL_ENV_BASE = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.path.join(VIRTUAL_ENV_BASE, r'.\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VIRTUAL_ENV_BASE, r'.\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']

# MAPBOX_KEY = 'pk.eyJ1IjoiZnJhbWVmMzE4IiwiYSI6ImNsNXh4NmExczAyODUzZG55anp1eHl3azQifQ.dUtvypHWk8UfMNgJe-aP8A'
# default_map_attrs = {  
#     "style": "mapbox://styles/mapbox/outdoors-v11",
#     "zoom": 13,
#     "center": [103.64099592061046, 16.04194018075107],
#     "cursor_style": 'pointer',
#     "marker_color": "red",
#     "rotate": False,
#     "geocoder": True,
#     "fullscreen_button": True,
#     "navigation_buttons": True,
#     "track_location_button": True, 
#     "readonly": True,
#     "placeholder": "Pick a location on map below", 
#     "language": "auto",
#     "message_404": "undefined address", 
#  }