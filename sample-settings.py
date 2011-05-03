#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
# encoding=utf-8

# -------------------------------------------------------------------- #
#                          MAIN CONFIGURATION                          #
# -------------------------------------------------------------------- #
TIME_ZONE="Africa/Kampala"
BASE_CSS="/static/rapidsms/stylesheets/layout.css"
# you should configure your database here before doing any real work.
# see: http://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rapidsms',
        'USER': 'www-data',
    }
}

ROUTER_URL = "http://127.0.0.1:13013/cgi-bin/sendsms?from=mynumber&username=user&password=pass&text=%(text)s&to=%(recipient)s&smsc=%(backend)s&dlr-url=http%%3A%%2F%%2Fstatus160.rapidsms.org%%2Frouter%%2Fdelivered%%2F%%3Fmessage_id%%3D%(id)s&dlr-mask=1"
REFRESH_WHITELIST_URL="http://127.0.0.1:13013/cgi-bin/refreshlist?username=user&password=pass&name=status160"
DEFAULT_RESPONSE = "This is status160, an emergency response system. There are currently no safety issues being tracked."

# to help you get started quickly, many django/rapidsms apps are enabled
# by default. you may wish to remove some and/or add your own.
INSTALLED_APPS = [

    # the essentials.
#    "django_nose",
    "djtables",
    "rapidsms",
    "mptt",
    "uni_form",
    "django_extensions",

    # common dependencies (which don't clutter up the ui).
    "rapidsms.contrib.handlers",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns), and a bunch of undocumented apps that
    # the AdminSite seems to explode without.
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.contenttypes",

    # the rapidsms contrib apps.
    "rapidsms.contrib.default",
    "rapidsms.contrib.registration",
    "eav",
    "code_generator",
    "simple_locations",
    "auth",
    "rapidsms_httprouter",
    "poll",
    "generic",
    "contact",
    "status160",
]

SMS_APPS = [
    "poll",
    "default",
]


# this rapidsms-specific setting defines which views are linked by the
# tabbed navigation. when adding an app to INSTALLED_APPS, you may wish
# to add it here, also, to expose it in the rapidsms ui.
RAPIDSMS_TABS = [
    ("status160-dashboard",                               "Dashboard"),
]


# -------------------------------------------------------------------- #
#                         BORING CONFIGURATION                         #
# -------------------------------------------------------------------- #


# debug mode is turned on as default, since rapidsms is under heavy
# development at the moment, and full stack traces are very useful
# when reporting bugs. don't forget to turn this off in production.
DEBUG = TEMPLATE_DEBUG = True 


# after login (which is handled by django.contrib.auth), redirect to the
# dashboard rather than 'accounts/profile' (the default).
LOGIN_REDIRECT_URL = "/status160/dashboard/"


# use django-nose to run tests. rapidsms contains lots of packages and
# modules which django does not find automatically, and importing them
# all manually is tiresome and error-prone.
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"


# for some reason this setting is blank in django's global_settings.py,
# but it is needed for static assets to be linkable.
MEDIA_URL = "/static/"
ADMIN_MEDIA_PREFIX="/static/media/"
# this is required for the django.contrib.sites tests to run, but also
# not included in global_settings.py, and is almost always ``1``.
# see: http://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = 3 


# the default log settings are very noisy.
LOG_LEVEL = "DEBUG"
LOG_FILE = "rapidsms.log"
LOG_FORMAT = "[%(name)s]: %(message)s"
LOG_SIZE = 8192  # 8192 bits = 8 kb
LOG_BACKUPS = 256  # number of logs to keep


# these weird dependencies should be handled by their respective apps,
# but they're not, so here they are. most of them are for django admin.
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
)

# -------------------------------------------------------------------- #
#                           HERE BE DRAGONS!                           #
#        these settings are pure hackery, and will go away soon        #
# -------------------------------------------------------------------- #


# these apps should not be started by rapidsms in your tests, however,
# the models and bootstrap will still be available through django.
TEST_EXCLUDED_APPS = [
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rapidsms",
    "rapidsms.contrib.ajax",
    "rapidsms.contrib.httptester",
]


TEMPLATE_LOADERS = (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django.template.loaders.eggs.Loader'
)

# the project-level url patterns
ROOT_URLCONF = "urls"


# since we might hit the database from any thread during testing, the
# in-memory sqlite database isn't sufficient. it spawns a separate
# virtual database for each thread, and syncdb is only called for the
# first. this leads to confusing "no such table" errors. We create
# a named temporary instance instead.
import os
import tempfile
import sys

if 'test' in sys.argv:
    for db_name in DATABASES:
        DATABASES[db_name]['TEST_NAME'] = os.path.join(
            tempfile.gettempdir(),
            "%s.rapidsms.test.sqlite3" % db_name)
