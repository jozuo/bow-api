import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, status
from pydantic import BaseModel, Field

from app.api.controllers.model import EmptyResponse, Message
from app.custom_logging import CustomLogger
from app.models.dog_model import DogModel

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class DogRequest(BaseModel):
    name: str = Field(..., title="名前")
    birth: Optional[int] = Field(None, title="誕生日(unixtime)", ge=0)
    gender: Optional[int] = Field(None, title="性別", ge=0)
    color: Optional[int] = Field(None, title="毛の色", ge=0)
    image_id: Optional[str] = Field(None, title="画像ID、事前にImageリソースで登録した際に発番されたID")
    order: Optional[int] = Field(None, title="画面表示順", ge=1)

    def to_model(self, owner_id: str) -> DogModel:
        # TODO ループ処理に置き換え
        model = DogModel()
        model.owner_id = owner_id
        model.dog_id = str(uuid.uuid4()).replace("-", "")
        model.name = self.name
        model.birth = self.birth
        model.gender = self.gender
        model.color = self.color
        model.image_id = self.image_id
        model.order = self.order
        return model


class DogResponse(DogRequest):
    id: str = Field(..., title="犬ID")
    updated_at: int = Field(..., title="更新日時(unixtime)")

    @classmethod
    def from_model(cls, model: DogModel) -> "DogResponse":
        # TODO ループ処理に置き換え
        response = DogResponse(
            id=model.dog_id,
            name=model.name,
            updated_at=model.updated_at,
        )

        if model.birth:
            response.birth = model.birth
        if model.gender:
            response.gender = model.gender
        if model.color:
            response.color = model.color
        if model.image_id:
            response.image_id = model.image_id
        if model.order:
            response.order = model.order
        return response


@router.get(
    "/",
    response_model=List[DogResponse],
    response_model_exclude_unset=True,
    summary="犬情報の一覧取得",
    description="オーナーに紐付く犬情報の一覧を取得します",
)
def list(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID")
) -> List[DogResponse]:
    return [DogResponse.from_model(x) for x in DogModel.query(hash_key=owner_id)]


@router.get(
    "/{id}",
    response_model=DogResponse,
    response_model_exclude_unset=True,
    summary="犬情報の1件取得",
    description="犬情報を1件取得します",
)
def get(
    owner_id: str = Path(
        ...,
        regex="^[a-z0-9]{32}$",
        description="オーナーID",
    ),
    dog_id: str = Path(..., regex="^[a-z0-9]{32}$", description="犬ID", alias="id"),
) -> DogResponse:

    try:
        return DogResponse.from_model(DogModel.get(hash_key=owner_id, range_key=dog_id))
    except DogModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dog not found.",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DogResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    summary="犬情報の登録",
    description="犬情報を登録します",
)
def post(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    request: DogRequest = Body(...),
) -> DogResponse:

    if is_name_exists(owner_id, request.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name is already exists.",
        )

    model = request.to_model(owner_id)
    model.save()
    return DogResponse.from_model(model)


@router.put(
    "/{id}",
    response_model=DogResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="犬情報の更新",
    description="犬情報を更新します",
)
def put(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    dog_id: str = Path(..., regex="^[a-z0-9]{32}$", description="犬ID", alias="id"),
    request: DogRequest = Body(...),
) -> DogResponse:

    try:
        model = DogModel.get(hash_key=owner_id, range_key=dog_id)
    except DogModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dog is not exist.",
        )

    for (key, value) in request.dict().items():
        setattr(model, key, value)
    model.updated_at = int(datetime.timestamp(datetime.now()))
    model.save()
    return DogResponse.from_model(model)


@router.delete(
    "/{id}",
    response_model=EmptyResponse,
    response_model_exclude_unset=True,
    summary="犬情報の削除",
    description="犬情報を削除します",
)
def delete(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID"),
    dog_id: str = Path(..., regex="^[a-z0-9]{32}$", description="犬ID", alias="id"),
) -> EmptyResponse:

    for model in DogModel.query(
        hash_key=owner_id, range_key_condition=DogModel.dog_id == dog_id
    ):
        model.delete()
    return EmptyResponse()


def is_name_exists(owner_id: str, name: str) -> bool:
    for model in DogModel.query(hash_key=owner_id, limit=1):
        if model.name == name:
            return True
    return False