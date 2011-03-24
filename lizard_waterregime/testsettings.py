import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s %(levelname)s %(message)s')

DEBUG = True
TEMPLATE_DEBUG = True
DATABASES = {
    # If you want to test with this database, put it in localsettings.py.
    'default': { #postgres testdatabase at N&S
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': '127.0.0.1',
        'NAME': 'waterregime',
        'USER': 'buildout',
        'PASSWORD': 'buildout'
        },
    }
SITE_ID = 1
INSTALLED_APPS = [
    'lizard_waterregime',
    'lizard_ui',
    'staticfiles',
    'compressor',
    'django_nose',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    ]
ROOT_URLCONF = 'lizard_waterregime.urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Used for django-staticfiles
STATIC_URL = '/static_media/'
TEMPLATE_CONTEXT_PROCESSORS = (
    # Default items.
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    # Needs to be added for django-staticfiles to allow you to use
    # {{ STATIC_URL }}myapp/my.css in your templates.
    'staticfiles.context_processors.static_url',
    )


try:
    # Import local settings that aren't stored in svn.
    from lizard_waterregime.local_testsettings import *
except ImportError:
    pass
