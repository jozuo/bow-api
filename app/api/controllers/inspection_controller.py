import os
from typing import List

import boto3
from fastapi import APIRouter, Body, File, HTTPException, UploadFile, status
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field

from app.api.controllers.common import owner_id_parameter
from app.api.controllers.model import Message
from app.custom_logging import CustomLogger
from app.logic.blood_inspection import parse_document
from app.logic.ocr import ocr
from app.models.inspection_result import InspectionResult

router = APIRouter()
logger = CustomLogger.getApplicationLogger()
s3 = boto3.resource("s3")

IMAGE_BUCKET = os.environ.get("IMAGE_BUCKET")


class AnalyzeResponse(BaseModel):
    item: str = Field(..., title="検査項目")
    value: str = Field(..., title="計測値")
    unit: str = Field(..., titie="単位")

    @classmethod
    def from_inspection_reusult(cls, result: InspectionResult) -> "AnalyzeResponse":
        return AnalyzeResponse(item=result.item, value=result.value, unit=result.unit)


@router.post(
    "/analize_image",
    response_model=List[AnalyzeResponse],
    response_model_exclude_unset=True,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
    summary="検査結果画像の解析",
    description="検査結果画像を解析して、解析結果を返却します。",
)
async def analize_image(
    owner_id: str = Depends(owner_id_parameter),
    kind: str = Body(..., regex="^(blood)$", title="検査種類"),
    files: List[UploadFile] = File(..., title="検査結果画像一覧"),
) -> List[AnalyzeResponse]:

    results: List[InspectionResult] = []
    for file in files:
        content_type = file.content_type
        if content_type not in ["image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"content-type [{content_type}] is not supported.",
            )

        contents = await file.read()
        obj = s3.Object(IMAGE_BUCKET, f"inspections/{owner_id}/file.filename")
        obj.put(Body=contents)

        # 血液検査以外に対応する場合は 条件分岐が必要
        results.extend(parse_document(ocr(binary=contents)))

    return [AnalyzeResponse.from_inspection_reusult(x) for x in results]
