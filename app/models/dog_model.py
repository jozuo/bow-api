from datetime import datetime

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.constants import is_offline, prefix


class DogModel(Model):
    class Meta:
        table_name = f"{prefix}-dog"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    owner_id = UnicodeAttribute(hash_key=True, null=False)
    dog_id = UnicodeAttribute(range_key=True, null=False)
    name = UnicodeAttribute(null=False)
    order = IntegerAttribute(null=False)
    birth = IntegerAttribute(null=True)
    gender = IntegerAttribute(null=True)
    color = IntegerAttribute(null=True)
    image_path = UnicodeAttribute(null=True)
    enabled = BooleanAttribute(null=False, default=True)
    updated_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
