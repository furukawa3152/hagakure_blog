from .base import *
DEBUG = True

SESSION_COOKIE_SECURE = True
ALLOWED_HOSTS = ['hagakurepgm.net', 'www.hagakurepgm.net','localhost']

try:
    from .local import *
except ImportError:
    pass

# 絵文字（😀 など）は4バイト。接続が utf8 のままだとコメント保存時に MariaDB が拒否する。
_database = DATABASES.get("default", {})
if _database.get("ENGINE", "").endswith("mysql"):
    _database.setdefault("OPTIONS", {})
    _database["OPTIONS"]["charset"] = "utf8mb4"