# -*- coding: utf-8 -*-
"""
Django settings for smartlicense project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

from os.path import dirname, abspath, join

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
SCRATCH_DIR = join(BASE_DIR, '.scratch')
SCRACTH_DB = join(SCRATCH_DIR, 'scratch.sqlite3')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3ka4^(c+fm7rw+@ttete34bt6tv3^8=r1!*_*-ovp1vu&qi=a9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = [('admin', 'admin@admin.org')]

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smartlicense.apps.SmartLicenseConfig',
    'django_markup',
    'martor',
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

ROOT_URLCONF = 'smartlicense.urls'

MEDIA_ROOT = SCRATCH_DIR
MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [join(BASE_DIR, 'smartlicense', 'templates')],
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

WSGI_APPLICATION = 'smartlicense.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SCRACTH_DB,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Mator
MARTOR_ENABLE_CONFIGS = {
    'imgur': 'false',    # to enable/disable imgur/custom uploader.
    'mention': 'false',  # to enable/disable mention
    'jquery': 'true',    # to include/revoke jquery (require for admin default django)
}

# Custom project settings
NODE_IP = '127.0.0.1'
NODE_PORT = '9718'
NODE_USER = 'testuser'
NODE_PWD = 'testpassword'

# Make sure deployment overrides settings
try:
    from smartlicense.settings.config import *
except Exception:
    print('No custom configuration found. Create a smartlicense/settings/config.py')
    import sys
    sys.exit(0)

