import re
from dataclasses import InitVar, dataclass
from typing import List, Optional

from app.models.inspection_result import InspectionResult


@dataclass
class Word:
    text: str
    width: float
    height: float
    left: float
    top: float


@dataclass
class BloodInspectionResult(InspectionResult):
    words: InitVar[List[str]]

    def __post_init__(self, items):
        # print(items)

        unit = ""
        for i, value in enumerate(items):
            if i == 0:
                self.item = value
            elif i == 1:
                self.value = self.__adjust_value(value)
            else:
                unit += value
        self.unit = self.__adjust_unit(unit)

    def __adjust_value(self, value: str) -> str:
        return value.replace("=", "").replace(" ", "")

    def __adjust_unit(self, unit: str) -> str:
        value = unit.replace(" ", "")
        if value.lower() in ["102/ul", "10²/ul"]:
            return "10^2/uL"
        if value.lower() in ["104/ul", "104/ul"]:
            return "10^4/uL"
        return value.replace("I", "l").replace(")", "l").replace("1", "l")


def parse_document(document: dict) -> List[BloodInspectionResult]:
    words: List[Word] = []
    for block in document["Blocks"]:
        if block["BlockType"] != "WORD":
            continue

        text = block["Text"]
        width = block["Geometry"]["BoundingBox"]["Width"]
        height = block["Geometry"]["BoundingBox"]["Height"]
        left = block["Geometry"]["BoundingBox"]["Left"]
        top = block["Geometry"]["BoundingBox"]["Top"]
        words.append(Word(text=text, width=width, height=height, left=left, top=top))

    prev_top: Optional[float] = None
    results: List[BloodInspectionResult] = []
    items: List[Word] = []
    for word in words:
        if prev_top is None:
            prev_top = word.top
        elif word.top - prev_top > 0.08:
            results.append(BloodInspectionResult([x.text for x in items]))
            prev_top = word.top
            items.clear()
        if len(items) == 0 and len(word.text) == 1:
            continue
        if word.text in ["=", "<", ">"]:
            continue
        items.append(word)

    if len(items) != 0:
        results.append(BloodInspectionResult([x.text for x in items]))

    if len(results) == 0 or (len(results) == 1 and len(results[0].unit) > 10):
        # 解析できなかったと判断してカラリストを返却
        return []
    return results


def _is_noise(block: dict, text: str) -> bool:
    # 領域が狭すぎる情報はノイズとして除去
    width = block["Geometry"]["BoundingBox"]["Width"]
    height = block["Geometry"]["BoundingBox"]["Height"]
    if width < 0.02 and height < 0.02:
        return True
    return False


def _is_item(word: str) -> bool:
    if re.search("^[A-Z]", word) is None:
        return False
    if "/" in word:
        return False
    if len(word) == 1:
        return False
    return True
