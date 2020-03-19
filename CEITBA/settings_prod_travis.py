from CEITBA.settings import *

DEBUG = False

ALLOWED_HOSTS = ['facturacion.ceitba.org.ar']

STATIC_ROOT = os.path.join(BASE_DIR, "static/")

SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ADMINS = [('John Doe', 'johndoe@email.com')]
SERVER_EMAIL = 'root@facturacion.ceitba.org.ar'
DEFAULT_FROM_EMAIL = 'CEITBA <webmaster@facturacion.ceitba.org.ar>'

EMAIL_HOST = 'localhost'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'travisdb',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

INSTALLED_APPS.remove('debug_toolbar')
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')
