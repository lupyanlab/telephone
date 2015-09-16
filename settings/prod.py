from .base import *

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['grunt.pedmiston.xyz', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'telephone',
        'USER': 'telephone',
        'PASSWORD': 'telephonepass',
        'HOST': environ.get('POSTGRESQL_HOST', 'localhost'),
        'PORT': '',
    },
}

BOWER_PATH = '/usr/local/bin/bower'
