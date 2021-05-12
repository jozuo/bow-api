from datetime import datetime

from pynamodb.attributes import ListAttribute, MapAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model
from pynamodb_attributes import IntegerAttribute

from app.constants import is_offline, prefix


class IdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "inspection-result-gsi1"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()

    id = UnicodeAttribute(hash_key=True, null=False)


class ResultMap(MapAttribute):
    item = UnicodeAttribute(null=False)
    value = UnicodeAttribute(null=False)
    unit = UnicodeAttribute(null=False)


class InspectionResultModel(Model):
    class Meta:
        table_name = f"{prefix}-inspection-result"
        region = "ap-northeast-1"
        billing_mode = "PAY_PER_REQUEST"
        if is_offline:
            host = "http://localhost:8000"

    key = UnicodeAttribute(hash_key=True, null=False)
    timestamp = IntegerAttribute(range_key=True, null=False)
    id = UnicodeAttribute(null=False)
    owner_id = UnicodeAttribute(null=False)
    dog_id = UnicodeAttribute(null=False)
    results = ListAttribute(of=ResultMap)
    updated_at = IntegerAttribute(
        null=False, default=int(datetime.timestamp(datetime.now()))
    )

    id_index = IdIndex()
