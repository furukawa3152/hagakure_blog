from .base import *
DEBUG = True

SESSION_COOKIE_SECURE = True
ALLOWED_HOSTS = ['hagakurepgm.net', 'www.hagakurepgm.net','localhost']

try:
    from .local import *
except ImportError:
    pass