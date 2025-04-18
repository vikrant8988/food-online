from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages
import os


# use this if setting up on Windows 10 with GDAL installed from OSGeo4W using defaults 
if os.name == 'nt':
    VIRTUAL_ENV_BASE = os.environ.get('VIRTUAL_ENV')
    if VIRTUAL_ENV_BASE:
        os.environ['PATH'] = os.path.join(VIRTUAL_ENV_BASE, 'Lib', 'site-packages', 'osgeo') + ';' + os.environ['PATH']
        os.environ['PROJ_LIB'] = os.path.join(VIRTUAL_ENV_BASE, 'Lib', 'site-packages', 'osgeo', 'data', 'proj')
        GDAL_LIBRARY_PATH = os.path.join(VIRTUAL_ENV_BASE, 'Lib', 'site-packages', 'osgeo', 'gdal.dll')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = []

# fallback url
LOGIN_URL = '/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.gis',
    'accounts',
    'vendor',
    'menu',
    'marketplace',
    'customers',
    'orders',
    
    'crequest'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'vendor.middleware.LoginRequiredMiddleware',
    'crequest.middleware.CrequestMiddleware', # custom middleware created to access request object in models.py
]

ROOT_URLCONF = 'foodonline_main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'accounts.context_processors.get_vendor',
                'marketplace.context_processor.get_cart_count',
                'accounts.context_processors.get_paypal_client_id'
            ],
        },
    },
]

WSGI_APPLICATION = 'foodonline_main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER':config('DB_USER'),
        'PASSWORD':config('DB_PASSWORD'),
        'HOST':config('DB_HOST'),
        'PORT': config('DB_PORT')
    }
}

AUTH_USER_MODEL = 'accounts.User'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'static'
STATICFILES_DIRS = [
    'foodonline_main/static'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}


# Email configuration
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Your Gmail
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Use an App Password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'foodOnline Marketplace <vikrant8988@gmail.com>'

PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

RZP_KEY_ID = config('RZP_KEY_ID')
RZP_KEY_SECRET = config('RZP_KEY_SECRET')
