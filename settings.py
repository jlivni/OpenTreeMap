import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))


SITE_ROOT = ''

#from settings_philadelphia import *
from settings_sandiego import *
#from settings_greenprint import *
#from settings_dctreekit import *
#from settings_sanfrancisco import *
#from settings_greenprint import *
#from settings_dctreekit import *

OTM_VERSION = "1.2"
API_VERSION = "0.1"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# sorl thumbnail settings
THUMBNAIL_DEBUG = True
THUMBNAIL_SUBDIR = '_thumbs'

AUTH_PROFILE_MODULE = 'profiles.userprofile'


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

ROOT_URLCONF = 'urls'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.load_template_source',
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    #"django.core.context_processors.auth",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'treemap.context_processors.site_root'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.csrf.middleware.CsrfViewMiddleware',
    'django.contrib.csrf.middleware.CsrfResponseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_reputation.middleware.ReputationMiddleware', 
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.databrowse',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.webdesign',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.comments',
    'treemap',
    'api',
    'registration',
    'template_utils',
    'profiles',
    'django_reputation',
    'tagging',
    'sorl.thumbnail',
    'classfaves',
    'qs_tiles',
    #'treekey',
    'badges',
    'pagination',
    'django_sorting',
    #'geopy_extensions',
)

try:
    from local_settings import *
except ImportError, exp:
    pass

LOGIN_URL = "%s/accounts/login" % SITE_ROOT
