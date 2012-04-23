import os
import sys
sys.path.append('/vagrant')
sys.path.append('/vagrant/markpro')
os.environ['DJANGO_SETTINGS_MODULE'] = 'markpro.settings'
os.environ["CELERY_LOADER"] = "django"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
import django.views.debug
def null_technical_500_response(request, exc_type, exc_value, tb):
    raise exc_type, exc_value, tb
django.views.debug.technical_500_response = null_technical_500_response
from werkzeug.debug import DebuggedApplication
application = DebuggedApplication(application, evalex=True)