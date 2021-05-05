import os
from datetime import timedelta, timezone

prefix = os.environ.get("TABLE_PREFIX")
is_offline = os.environ.get("IS_OFFLINE")
JST = timezone(timedelta(hours=9), "JST")
