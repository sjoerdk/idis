import os
import re
from datetime import timedelta
from distutils.util import strtobool as strtobool_i
from django.contrib.messages import constants as messages


def strtobool(val) -> bool:
    """Return disutils.util.strtobool as a boolean."""
    return bool(strtobool_i(val))


DEBUG = strtobool(os.environ.get("DEBUG", "True"))

COMMIT_ID = os.environ.get("COMMIT_ID", "unknown")

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Who gets the 404 notifications?
manager_email = os.environ.get("MANAGER_EMAIL", None)
if manager_email:
    MANAGERS = [("Manager", manager_email)]

IGNORABLE_404_URLS = [
    re.compile(r".*\.(php|cgi|asp).*"),
    re.compile(r"^/phpmyadmin.*"),
    re.compile(r"^/gen204.*"),
    re.compile(r"^/wp-content.*"),
    re.compile(r"^/wp.*"),
    re.compile(r".*/trackback.*"),
    re.compile(r"^/site/.*"),
    re.compile(r"^/media/cache/.*"),
]

# Used as starting points for various other paths. realpath(__file__) starts in
# the config dir. We need to  go one dir higher so path.join("..")
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
APPS_DIR = os.path.join(SITE_ROOT, "idis")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "idis"),
        "USER": os.environ.get("POSTGRES_USER", "idis"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "secretpassword"),
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PORT": "",
    }
}

EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = strtobool(os.environ.get("EMAIL_USE_TLS", "False"))
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "webmaster@localhost"
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "root@localhost")

ANONYMOUS_USER_NAME = "AnonymousUser"
REGISTERED_USERS_GROUP_NAME = "__registered_users_group__"
REGISTERED_AND_ANON_USERS_GROUP_NAME = "__registered_and_anonymous_users__"

AUTH_PROFILE_MODULE = "profiles.UserProfile"

LOGIN_REDIRECT_URL = "/accounts/login-redirect/"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL

# Do not give message popups saying "you have been logged out". Users are expected
# to know they have been logged out when they click the logout button
USERENA_USE_MESSAGES = (False,)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = int(os.environ.get("SITE_ID", "1"))

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

##############################################################################
#
# Storage
#
##############################################################################
# Subdirectories on root for various files
JQFILEUPLOAD_UPLOAD_SUBIDRECTORY = "jqfileupload"
IMAGE_FILES_SUBDIRECTORY = "images"
EVALUATION_FILES_SUBDIRECTORY = "evaluation"


##############################################################################
#
# Caching
#
##############################################################################

CACHES = {
    "default": {
        "BACKEND": "speedinfo.backends.proxy_cache",
        "CACHE_BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "memcached:11211",
    }
}
SPEEDINFO_STORAGE = "speedinfo.storage.cache.storage.CacheStorage"

ROOT_URLCONF = "config.urls"
DEFAULT_SCHEME = os.environ.get("DEFAULT_SCHEME", "https")

SESSION_COOKIE_DOMAIN = os.environ.get(
    "SESSION_COOKIE_DOMAIN", ".idis.localhost"
)
# We're always running behind a proxy so set these to true
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Set the allowed hosts to the cookie domain
ALLOWED_HOSTS = [SESSION_COOKIE_DOMAIN, "web"]

# Security options
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = strtobool(
    os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False")
)
SECURE_HSTS_PRELOAD = strtobool(os.environ.get("SECURE_HSTS_PRELOAD", "True"))
SECURE_CONTENT_TYPE_NOSNIFF = strtobool(
    os.environ.get("SECURE_CONTENT_TYPE_NOSNIFF", "False")
)
SECURE_BROWSER_XSS_FILTER = strtobool(
    os.environ.get("SECURE_BROWSER_XSS_FILTER", "False")
)
X_FRAME_OPTIONS = os.environ.get("X_FRAME_OPTIONS", "SAMEORIGIN")
SECURE_REFERRER_POLICY = os.environ.get(
    "SECURE_REFERRER_POLICY", "same-origin"
)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = "/static/"

STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "")
STATIC_URL = f"{STATIC_HOST}/static/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Vendored static files will be put here
STATICFILES_DIRS = ["/opt/static/"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = "/media/"
MEDIA_URL = f"{STATIC_HOST}/media/"


# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "d=%^l=xa02an9jn-$!*hy1)5yox$a-$2(ejt-2smimh=j4%8*b"
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR)],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",  # Keep security at top
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Keep whitenoise after security and before all else
    "corsheaders.middleware.CorsMiddleware",  # Keep CORS near the top
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    # Keep BrokenLinkEmailsMiddleware near the top
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    # subdomain_middleware after CurrentSiteMiddleware
    # Flatpage fallback almost last
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    # speedinfo at the end but before FetchFromCacheMiddleware
    "speedinfo.middleware.ProfilerMiddleware",
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "config.wsgi.application"

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # Keep whitenoise above staticfiles
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.postgres",
    "django.contrib.flatpages",
]

THIRD_PARTY_APPS = [
    "django_celery_results",  # database results backend
    "django_celery_beat",  # periodic tasks
    "djcelery_email",  # asynchronous emails
    "userena",  # user profiles
    "guardian",  # userena dependency, per object permissions
    "easy_thumbnails",  # userena dependency
    "rest_framework",  # provides REST API
    "rest_framework.authtoken",  # token auth for REST API
    "crispy_forms",  # bootstrap forms
    "favicon",  # favicon management
    "django_select2",  # for multiple choice widgets
    "dal",  # for autocompletion of selection fields
    "dal_select2",  # for autocompletion of selection fields
    "django_extensions",  # custom extensions
    "simple_history",  # for object history
    "corsheaders",  # to allow api communication from subdomains
    "speedinfo",  # for profiling views
    "drf_yasg",
    "markdownx",  # for editing markdown
]

LOCAL_APPS = ["idis.core", "idis.jobs", "idis.profiles", "idis.pipeline"]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

ADMIN_URL = f'{os.environ.get("DJANGO_ADMIN_URL", "django-admin")}/'

AUTHENTICATION_BACKENDS = (
    "userena.backends.UserenaAuthenticationBackend",
    "guardian.backends.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", ""
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", ""
)

# Django 1.6 introduced a new test runner, use it
TEST_RUNNER = "django.test.runner.DiscoverRunner"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# A sample logging configuration. More info in configuration can be found at
# https://docs.djangoproject.com/en/dev/topics/logging/ .
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler"}
    },
    "loggers": {
        "idis": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": True,
        },
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "werkzeug": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PAGINATION_CLASS": "idis.api.pagination.MaxLimit1000OffsetPagination",
    "PAGE_SIZE": 100,
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}


CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "django-db")
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_SOFT_TIME_LIMIT = int(
    os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", "7200")
)
CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", "7260"))

CONTAINER_EXEC_DOCKER_BASE_URL = os.environ.get(
    "CONTAINER_EXEC_DOCKER_BASE_URL", "unix://var/run/docker.sock"
)
CONTAINER_EXEC_DOCKER_TLSVERIFY = strtobool(
    os.environ.get("CONTAINER_EXEC_DOCKER_TLSVERIFY", "False")
)
CONTAINER_EXEC_DOCKER_TLSCACERT = os.environ.get(
    "CONTAINER_EXEC_DOCKER_TLSCACERT", ""
)
CONTAINER_EXEC_DOCKER_TLSCERT = os.environ.get(
    "CONTAINER_EXEC_DOCKER_TLSCERT", ""
)
CONTAINER_EXEC_DOCKER_TLSKEY = os.environ.get(
    "CONTAINER_EXEC_DOCKER_TLSKEY", ""
)
CONTAINER_EXEC_MEMORY_LIMIT = os.environ.get(
    "CONTAINER_EXEC_MEMORY_LIMIT", "4g"
)
CONTAINER_EXEC_IO_IMAGE = "alpine:3.9"
CONTAINER_EXEC_IO_SHA256 = (
    "sha256:82f67be598ebc8d968137c18521fe174ca6afc9b542aa5773c32b3a3970e647c"
)
CONTAINER_EXEC_CPU_QUOTA = int(
    os.environ.get("CONTAINER_EXEC_CPU_QUOTA", "100000")
)
CONTAINER_EXEC_CPU_PERIOD = int(
    os.environ.get("CONTAINER_EXEC_CPU_PERIOD", "100000")
)
CONTAINER_EXEC_PIDS_LIMIT = int(
    os.environ.get("CONTAINER_EXEC_PIDS_LIMIT", "128")
)
CONTAINER_EXEC_CPU_SHARES = int(
    os.environ.get("CONTAINER_EXEC_CPU_SHARES", "1024")  # Default weight
)
CONTAINER_EXEC_DOCKER_RUNTIME = os.environ.get(
    "CONTAINER_EXEC_DOCKER_RUNTIME", None
)

CELERY_BEAT_SCHEDULE = {
    "run_celery_test": {
        "task": "idis.pipeline.tasks.run_test_task",
        "schedule": timedelta(seconds=2),
    },
}

CELERY_TASK_ROUTES = {}

# The name of the group whose members can edit jobs and destinations
JOB_ADMINS_GROUP_NAME = "job_admins"

# for IDIS
IDIS_CTP_INPUT_FOLDER = os.environ.get(
    "IDIS_CTP_INPUT_FOLDER", "/tmp/ctp/input"
)
IDIS_CTP_OUTPUT_FOLDER = os.environ.get(
    "IDIS_CTP_OUTPUT_FOLDER", "/tmp/ctp/output"
)
IDIS_PRE_FETCHING_FOLDER = os.environ.get(
    "IDIS_PRE_FETCHING_FOLDER", "/tmp/ctp/pre_fetching"
)


# Set which template pack to use for forms
CRISPY_TEMPLATE_PACK = "bootstrap4"

# When using bootstrap error messages need to be renamed to danger
MESSAGE_TAGS = {messages.ERROR: "danger"}

# The maximum size of all the files in an upload session in bytes
UPLOAD_SESSION_MAX_BYTES = 15_000_000_000

# Tile size in pixels to be used when creating dzi for tif files
DZI_TILE_SIZE = 2560

ENABLE_DEBUG_TOOLBAR = False

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    LOGGING["loggers"]["idis"]["level"] = "DEBUG"

    if ENABLE_DEBUG_TOOLBAR:
        INSTALLED_APPS += ("debug_toolbar",)

        MIDDLEWARE = (
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            *MIDDLEWARE,
        )

        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_TOOLBAR_CALLBACK": "config.toolbar_callback"
        }
