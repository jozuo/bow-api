from typing import List

from requests.models import Response


def assert_valication_error(response: Response, loc: List[str], msg: str) -> None:
    error = response.json()["detail"][0]
    assert error["loc"] == loc
    assert error["msg"] == msg
