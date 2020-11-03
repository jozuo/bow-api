import os

from fastapi.testclient import TestClient

from app.api.main import app
from app.models.owner_model import OwnerModel
from tests.test_util import assert_valication_error

EXIST_EMAIL = "user1@test.com"
NOT_EXIST_EMAIL = "user2@test.com"
ILLEGAL_EMAIL = "hoge@page"


class TestOwnerController:
    @classmethod
    def setup_class(cls):
        os.environ["LOG_LEVEL"] = "WARNING"

        for model in OwnerModel.scan():
            model.delete()

        model = OwnerModel()
        model.id = "00000000000000000000000000000000"
        model.email = EXIST_EMAIL
        model.save()

    @classmethod
    def teardown_class(cls):
        for model in OwnerModel.scan():
            model.delete()

    def setup_method(self, method):
        self.client = TestClient(app)

    def test_search_01(self):
        """
        メールアドレスによるオーナー検索
        メールアドレスが存在する場合
        """
        response = self.client.get(f"/owners/search?email={EXIST_EMAIL}")
        body = response.json()
        assert response.status_code == 200
        assert body["id"] == "00000000000000000000000000000000"
        assert body["email"] == EXIST_EMAIL

    def test_search_02(self):
        """
        メールアドレスによるオーナー検索
        メールアドレスが存在しない場合
        """
        response = self.client.get(f"/owners/search?email={NOT_EXIST_EMAIL}")
        body = response.json()
        assert response.status_code == 404
        assert body["detail"] == "owner not found."

    def test_search_03(self):
        """
        メールアドレスによるオーナー検索
        メールアドレスが不正な場合
        """
        response = self.client.get(f"/owners/search?email={ILLEGAL_EMAIL}")
        assert response.status_code == 422
        assert_valication_error(
            response, ["query", "email"], "value is not a valid email address"
        )

    def test_post_01(self):
        """
        オーナー登録
        新規メールアドレスの場合
        """
        body = {"email": "newuser@test.com"}
        response = self.client.post("/owners/", json=body)
        body = response.json()
        assert response.status_code == 201
        assert "id" in body
        assert body["email"] == "newuser@test.com"

    def test_post_02(self):
        """
        オーナー登録
        既に登録されているメールアドレスの場合
        """
        body = {"email": EXIST_EMAIL}
        response = self.client.post("/owners/", json=body)
        body = response.json()
        assert response.status_code == 400
        assert body["detail"] == "email is already exists."

    def test_post_03(self):
        """
        オーナー登録
        メールアドレスが不正な場合
        """
        body = {"email": ILLEGAL_EMAIL}
        response = self.client.post("/owners/", json=body)
        body = response.json()
        assert response.status_code == 422
        assert_valication_error(
            response, ["body", "email"], "value is not a valid email address"
        )
