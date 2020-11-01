import os
from datetime import datetime

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

prefix = os.environ.get("TABLE_PREFIX")
is_offline = os.environ.get("IS_OFFLINE")

print(f"prefix: {prefix}")
print(f"is_offline: {is_offline}")


class OwnerModel(Model):
    class Meta:
        table_name = f"{prefix}-owner"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    id = UnicodeAttribute(hash_key=True, null=False)
    email = UnicodeAttribute(null=False)
    created_at = NumberAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
