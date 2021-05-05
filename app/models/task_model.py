from datetime import datetime

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.constants import is_offline, prefix


class TaskModel(Model):
    class Meta:
        table_name = f"{prefix}-task"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    owner_id = UnicodeAttribute(hash_key=True, null=False)
    task_id = UnicodeAttribute(range_key=True, null=False)
    icon_no = IntegerAttribute(null=False)
    title = UnicodeAttribute(null=False)
    order = IntegerAttribute(null=False)
    enabled = BooleanAttribute(null=False, default=True)
    updated_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
