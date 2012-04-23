import os
import djcelery
djcelery.setup_loader()

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "markpromq"
BROKER_PASSWORD = "markpro"
BROKER_VHOST = "markpro"

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'topic',
        'binding_key': 'tasks.#'
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = {
    'aquarhead' : 'aquarhead_admin',
    'pioneer' : 'langmanking',
}

USERS = {
    'admin' : '123456',
}

WEIBO_KEY = '3718858912'
WEIBO_SECRET = '48c5c054d71ff3d9812706c5a5ef1651'
WEIBO_CALLBACK = "http://127.0.0.1:8000/weibo_callback"
TQQ_KEY = '801083681'
TQQ_SECRET = '545169f71fdb685e5aa3389bde21c888'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/Users/Pioneer/www/database/markpro.db',
        #'NAME': 'markpro',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'zh-CN'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = '/Users/Pioneer/www/markpro/media'

MEDIA_URL = 'http://127.0.0.1:8000/media/'

STATIC_ROOT = ''

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    '/Users/Pioneer/www/markpro/static',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'a78dfsx38fj6xvh2=-ej0xnx67hdd2bn2^%s(s=$fl!*m=@g7$'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'markpro.urls'

TEMPLATE_DIRS = (
    '/Users/Pioneer/www/markpro/templates',
)

INSTALLED_APPS = (
    
    # Plug-ins
    # 'south',
    'djcelery',
    
    # Django
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Project related
    'brands',
    'blogs',
    'mblogs',
    'stores',
    'results',
)