import os
from typing import Optional

from fastapi.testclient import TestClient
from requests.models import Response

from app.api.main import app

OWNER_ID_EXIST = "fdc8e0aaac134c6e87b299171f531103"
OWNER_ID_NOT_EXIST = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"


class TestEventCongroller:
    @classmethod
    def setup_class(cls):
        os.environ["LOG_LEVEL"] = "WARNING"

    def setup_method(self):
        self.client = TestClient(app)
        self.headers = {"x-api-key": "hogehoge"}

    def get(self, url: str, params: Optional[dict]) -> Response:
        return self.client.get(url, headers=self.headers, params=params)

    def test_list_01(self):
        """一覧取得
        存在しないオーナーの場合、404が返却されること
        """
        # -- exercise
        params = {"from": 1613259000, "to": 1613259001}
        response = self.get(f"/owners/{OWNER_ID_NOT_EXIST}/events/", params=params)
        body = response.json()
        # -- verify
        assert response.status_code == 404
        assert body == {"detail": "owner not found."}

    def test_list_02(self):
        """一覧取得
        指定期間に該当するデータが無い場合、空レスポンスが返却されること
        """
        # -- exercise
        params = {"from": 1613259000, "to": 1613259001}
        response = self.get(f"/owners/{OWNER_ID_EXIST}/events/", params=params)
        body = response.json()
        # -- verify
        assert response.status_code == 200
        assert len(body) == 0

    def test_list_03(self):
        """一覧取得
        指定期間に該当するデータが存在する場合、「犬の表示順 → タスクのタイムスタンプ」でソートされた一覧が取得できること
        """
        # -- exercise
        params = {"from": 1613259267, "to": 1613259867}
        response = self.get(f"/owners/{OWNER_ID_EXIST}/events/", params=params)
        body = response.json()
        # -- verify
        assert response.status_code == 200
        assert len(body) == 4

        assert body[0]["id"] == "12b01d976cee4f23b2bdcea90a7312e0"
        assert body[1]["id"] == "d5c448961ac94a95b762efd5d504a92e"
        assert body[2]["id"] == "411c14d194434425aedc260dde8fa534"
        assert body[3]["id"] == "be65e6661f2d437d9a8274ea77659c59"
