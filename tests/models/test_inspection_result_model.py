import json

import pytest

from app.models.inspection_result_model import InspectionResultModel


@pytest.fixture(autouse=True)
def setup_dynamodb(datadir):
    meta = getattr(InspectionResultModel, "Meta")
    setattr(meta, "table_name", getattr(meta, "table_name").replace("local", "test"))
    InspectionResultModel.create_table(wait=True)

    for item in json.loads((datadir / "base.json").read_text()):
        InspectionResultModel(**item).save()

    yield
    InspectionResultModel.delete_table()


class TestInspectionResultModel:
    def test_find_by_key_01(self):
        """
        オーナーと犬を指定した検索。
        - 複数レコード取得できる場合
        """

        # -- setup
        owner_id = "owner1"
        dog_id = "dog1"

        # -- exercise
        actuals = [
            x for x in InspectionResultModel.query(hash_key=f"{owner_id}-{dog_id}")
        ]

        # -- verify
        assert len(actuals) == 2
        _assert_record(actuals[0], owner_id, dog_id, 111111111, 2)
        _assert_record(actuals[1], owner_id, dog_id, 111111222, 1)

    def test_find_by_key_02(self):
        """
        オーナーと犬を指定した検索。
        - オーナー違いで レコードが取得できない場合
        """

        # -- setup
        owner_id = "owner3"
        dog_id = "dog1"

        # -- exercise
        actuals = [
            x for x in InspectionResultModel.query(hash_key=f"{owner_id}-{dog_id}")
        ]

        # -- verify
        assert len(actuals) == 0

    def test_find_by_key_03(self):
        """
        オーナーと犬を指定した検索。
        - 犬違いで レコードが取得できない場合
        """

        # -- setup
        owner_id = "owner1"
        dog_id = "dog3"

        # -- exercise
        actuals = [
            x for x in InspectionResultModel.query(hash_key=f"{owner_id}-{dog_id}")
        ]

        # -- verify
        assert len(actuals) == 0

    def test_find_by_id_01(self):
        """
        IDを指定した検索
        - 取得できる場合
        """

        # -- setup
        owner_id = "owner1"
        dog_id = "dog1"
        timestamp = 111111111
        id = f"{owner_id}-{dog_id}-{timestamp}"

        # -- exercise
        actuals = [x for x in InspectionResultModel.id_index.query(hash_key=f"{id}")]

        # -- verify
        assert len(actuals) == 1
        _assert_record(actuals[0], owner_id, dog_id, timestamp, 2)

    def test_find_by_id_02(self):
        """
        IDを指定した検索
        - 取得できない場合
        """

        # -- setup
        owner_id = "owner3"
        dog_id = "dog1"
        timestamp = 111111111
        id = f"{owner_id}-{dog_id}-{timestamp}"

        # -- exercise
        actuals = [x for x in InspectionResultModel.id_index.query(hash_key=f"{id}")]

        # -- verify
        assert len(actuals) == 0


def _assert_record(
    actual: InspectionResultModel,
    owner_id: str,
    dog_id: str,
    timestamp: int,
    results_count: int,
) -> None:
    assert actual.key == f"{owner_id}-{dog_id}"
    assert actual.timestamp == timestamp
    assert actual.id == f"{owner_id}-{dog_id}-{timestamp}"
    assert actual.owner_id == owner_id
    assert actual.dog_id == dog_id
    assert len(actual.results) == results_count
