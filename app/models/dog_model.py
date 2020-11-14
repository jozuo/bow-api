import os
from datetime import datetime

from pynamodb.attributes import UnicodeAttribute, BooleanAttribute
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

prefix = os.environ.get("TABLE_PREFIX")
is_offline = os.environ.get("IS_OFFLINE")


class DogModel(Model):
    class Meta:
        table_name = f"{prefix}-dog"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    owner_id = UnicodeAttribute(hash_key=True, null=False)
    dog_id = UnicodeAttribute(range_key=True, null=False)
    name = UnicodeAttribute(null=False)
    birth = IntegerAttribute(null=True)
    gender = IntegerAttribute(null=True)
    color = IntegerAttribute(null=True)
    image_path = UnicodeAttribute(null=True)
    order = IntegerAttribute(null=True)
    enabled = BooleanAttribute(null=False, default=True)
    updated_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
