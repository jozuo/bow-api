import os
from datetime import datetime

from fastapi.testclient import TestClient
from requests.models import Response

from app.api.main import app
from app.models.dog_model import DogModel
from app.models.owner_model import OwnerModel

OWNER_ID_1 = "00000000000000000000000000000000"
OWNER_ID_2 = "22222222222222222222222222222222"
OWNER_ID_3 = "33333333333333333333333333333333"
DOG_ID_MIN = "44444444444444444444444444444444"
DOG_ID_MAX = "55555555555555555555555555555555"
DOG_ID_NOT_EXIST = "66666666666666666666666666666666"
UPDATED_AT = int(datetime.timestamp(datetime.now()))


class TestDogCongroller:
    @classmethod
    def setup_class(cls):
        os.environ["LOG_LEVEL"] = "WARNING"
        try:
            OwnerModel.get(hash_key=OWNER_ID_1)
        except OwnerModel.DoesNotExist:
            owner = OwnerModel(id=OWNER_ID_1)
            owner.email = "user1@test.com"
            owner.save()

        try:
            OwnerModel.get(hash_key=OWNER_ID_2)
        except OwnerModel.DoesNotExist:
            owner = OwnerModel(id=OWNER_ID_2)
            owner.email = "user2@test.com"
            owner.save()

    def setup_method(self):
        self.client = TestClient(app)
        self.headers = {"x-api-key": "hogehoge"}

        # 必須項目のみのレコード作成
        for min_model in DogModel.query(
            hash_key=OWNER_ID_1, range_key_condition=DogModel.dog_id == DOG_ID_MIN
        ):
            min_model.delete()
        min_model = self.__create_model_min(
            owner_id=OWNER_ID_1, dog_id=DOG_ID_MIN, updated_at=UPDATED_AT
        )
        min_model.save()

        # 全項目設定されているレコード作成
        for max_model in DogModel.query(
            hash_key=OWNER_ID_1, range_key_condition=DogModel.dog_id == DOG_ID_MAX
        ):
            max_model.delete()
        max_model = self.__create_model_max(
            owner_id=OWNER_ID_1, dog_id=DOG_ID_MAX, updated_at=UPDATED_AT
        )
        max_model.save()

    def get(self, url: str) -> Response:
        return self.client.get(url, headers=self.headers)

    def test_list_01(self):
        """
        犬情報の一覧取得
        ユーザー、犬情報供に存在する場合
        """
        response = self.get(f"/owners/{OWNER_ID_1}/dogs/")
        body = response.json()
        assert response.status_code == 200

        assert len(body) == 2
        assert body[0]["id"] == DOG_ID_MIN
        assert body[0]["name"] == f"{body[0]['id']}-name"
        assert body[0]["updated_at"] == UPDATED_AT
        assert body[0]["image_path"] == "image/path"
        assert "order" in body[0]
        assert "birth" not in body[0]
        assert "gender" not in body[0]
        assert "color" not in body[0]
        assert "image" not in body[0]

        assert body[1]["id"] == DOG_ID_MAX
        assert body[1]["name"] == f"{body[1]['id']}-name"
        assert body[1]["updated_at"] == UPDATED_AT
        assert body[1]["image_path"] == "image/path"
        assert "order" in body[1]
        assert "birth" in body[1]
        assert "gender" in body[1]
        assert "color" in body[1]

    def test_list_02(self):
        """
        犬情報の一覧取得
        犬情報が登録されていないオーナーの場合
        """
        response = self.get(f"/owners/{OWNER_ID_2}/dogs/")
        body = response.json()
        assert response.status_code == 200
        assert len(body) == 0

    def test_list_03(self):
        """
        犬情報の一覧取得
        オーナーが存在しない場合
        """
        response = self.get(f"/owners/{OWNER_ID_3}/dogs/")
        body = response.json()
        assert response.status_code == 404
        assert body == {"detail": "owner not found."}

    def test_get_01(self):
        """
        犬情報の1件取得
        情報が取得できる場合
        """
        response = self.get(f"/owners/{OWNER_ID_1}/dogs/{DOG_ID_MIN}")
        body = response.json()
        assert response.status_code == 200
        assert body["id"] == DOG_ID_MIN
        assert body["name"] == f"{body['id']}-name"
        assert body["updated_at"] == UPDATED_AT
        assert body["image_path"] == "image/path"
        assert "order" in body
        assert "birth" not in body
        assert "gender" not in body
        assert "color" not in body

    def test_get_02(self):
        """
        犬情報の1件取得
        犬情報が存在しないIDが指定された場合
        """
        response = self.get(f"/owners/{OWNER_ID_1}/dogs/{DOG_ID_NOT_EXIST}")
        body = response.json()
        assert response.status_code == 404
        assert body == {"detail": "dog not found."}

    def test_get_03(self):
        """
        犬情報の1件取得
        オーナー情報が存在しないIDが指定された場合
        """
        response = self.get(f"/owners/{OWNER_ID_3}/dogs/{DOG_ID_MIN}")
        body = response.json()
        assert response.status_code == 404
        assert body == {"detail": "owner not found."}

    def __create_model_min(self, owner_id: str, dog_id: str, updated_at: int):
        name = f"{dog_id}-name"
        return DogModel(
            owner_id=owner_id,
            dog_id=dog_id,
            name=name,
            image_path="image/path",
            order=1,
            updated_at=updated_at,
        )

    def __create_model_max(self, owner_id: str, dog_id: str, updated_at: int):
        name = f"{dog_id}-name"
        return DogModel(
            owner_id=owner_id,
            dog_id=dog_id,
            name=name,
            updated_at=updated_at,
            birth=1111111111,
            gender=1,
            color=1,
            image_path="image/path",
            order=1,
        )
