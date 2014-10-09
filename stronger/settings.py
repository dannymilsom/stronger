"""
Django settings for stronger django project.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

try:
    from stronger.secret_settings import *
except ImportError:
    # this is a automatically generated secret key included for convinence
    # via http://www.miniwebtool.com/django-secret-key-generator
    SECRET_KEY = 'cbph62=513s$ui9eqow+0#am13_n0i^&mn8hogff$-a%mu0ac0'

try:
    from production_settings import *
except ImportError:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '+nb-p4zmahxhkwa1vbr1-m*_xxk%4i&i*iacm5@f)qhzll6!1-'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    TEMPLATE_DEBUG = True

    ALLOWED_HOSTS = []

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

LOCAL_APPS = (
    'stronger',
)

THIRD_PARTY_APPS = (
    'south',
    'rest_framework',
    'rest_framework.authtoken',
)

INSTALLED_APPS = DEFAULT_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'stronger.context_processors.login_form',
    'stronger.context_processors.signup_form',
    'stronger.context_processors.friend_form',
    'stronger.context_processors.setting_variables',
)

ROOT_URLCONF = 'stronger.urls'

WSGI_APPLICATION = 'stronger.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

#USE_L10N = True

USE_TZ = True

DATE_FORMAT = "N j Y"

DATETIME_FORMAT = "N j Y"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
)

# overwriting the default user profile and table to include extra fields
AUTH_USER_MODEL = 'stronger.StrongerUser'

LOGIN_URL = '/login'

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    )
}

SITE_ID = 1

INTERNAL_IPS = ('127.0.0.1',)

GITHUB_URL = 'https://github.com/dannymilsom/stronger'

