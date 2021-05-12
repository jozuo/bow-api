from datetime import datetime

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.constants import is_offline, prefix


class OwnerModel(Model):
    class Meta:
        table_name = f"{prefix}-owner"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    id = UnicodeAttribute(hash_key=True, null=False)
    email = UnicodeAttribute(null=False)
    created_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
