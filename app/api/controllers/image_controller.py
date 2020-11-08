import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Path,
    Query,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from app.api.controllers.model import EmptyResponse, Message
from app.custom_logging import CustomLogger

IMAGE_BUCKET = os.environ.get("IMAGE_BUCKET")

router = APIRouter()
logger = CustomLogger.getApplicationLogger()
s3 = boto3.resource("s3")


class ImageResponse(BaseModel):
    image_path: str = Field(..., title="画像パス")


class ImageDataResponse(BaseModel):
    data: bytes = Field(..., title="画像データ")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ImageResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    summary="画像情報の登録",
    description="画像情報を登録します",
)
async def post(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    file: UploadFile = File(..., description="画像ファイルデータ"),
):

    content_type = file.content_type
    if content_type not in ["image/png", "image/gif", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"content-type [{content_type}] is not supported.",
        )

    contents = await file.read()
    now = datetime.now()
    id = f"{str(uuid.uuid4()).replace('-', '')}.{content_type.split('/')[-1]}"
    image_path = f'{now.strftime("%Y")}{now.strftime("%m")}{now.strftime("%d")}/{now.strftime("%H")}/{id}'

    obj = s3.Object(IMAGE_BUCKET, f"{owner_id}/{image_path}")
    obj.put(Body=contents)

    return ImageResponse(image_path=image_path)


@router.get(
    "/",
    response_description="画像データ(バイナリ)",
    response_class=Response,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="画像データの取得",
    description="画像データ(バイナリ)を取得します",
)
def get(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    image_path: str = Query(..., regex="^[a-z0-9/.]+$", description="画像パス"),
):

    try:
        obj = s3.Object(IMAGE_BUCKET, f"{owner_id}/{image_path}")
        bytes_image = obj.get()["Body"].read()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="image is not exist.",
            )
        else:
            raise e

    extension = image_path.split(".")[-1]
    return Response(
        content=bytes_image,
        media_type=f"image/{extension}",
        headers={"content-type": f"image/{extension}"},
    )


@router.delete(
    "/",
    response_model=EmptyResponse,
    response_model_exclude_unset=True,
    summary="画像データの削除",
    description="画像データを削除します",
)
def delete(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    image_path: str = Query(..., regex="^[a-z0-9/.]+$", description="画像パス"),
):
    try:
        obj = s3.Object(IMAGE_BUCKET, f"{owner_id}/{image_path}")
        obj.delete()
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchKey":
            raise e

    return EmptyResponse()
