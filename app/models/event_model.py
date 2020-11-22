import os
from datetime import datetime

from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import AllProjection, LocalSecondaryIndex
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

prefix = os.environ.get("TABLE_PREFIX")
is_offline = os.environ.get("IS_OFFLINE")


class TimestampIndex(LocalSecondaryIndex):
    class Meta:
        index_name = "event-lsi1"
        read_capacity_units = 2
        write_capacity_units = 2
        projection = AllProjection()

    owner_id = UnicodeAttribute(hash_key=True, null=False)
    timestamp = IntegerAttribute(range_key=True, null=False)


class EventModel(Model):
    class Meta:
        table_name = f"{prefix}-event"
        region = "ap-northeast-1"
        if is_offline:
            host = "http://localhost:8000"

    owner_id = UnicodeAttribute(hash_key=True, null=False)
    event_id = UnicodeAttribute(range_key=True, null=False)
    timestamp = IntegerAttribute(null=False)
    timestamp_index = TimestampIndex()
    task_id = UnicodeAttribute(null=False)
    dog_id = UnicodeAttribute(null=False)
    updated_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )
