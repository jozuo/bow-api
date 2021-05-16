import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, status
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field

from app.api.controllers.common import owner_id_parameter
from app.api.controllers.model import EmptyResponse, Message
from app.custom_logging import CustomLogger
from app.models.dog_model import DogModel

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class DogRequest(BaseModel):
    name: str = Field(..., title="名前")
    order: int = Field(..., title="画面表示順", ge=1)
    birth: Optional[int] = Field(None, title="誕生日(unixtime)", ge=0)
    gender: Optional[int] = Field(None, title="性別", ge=0)
    color: Optional[int] = Field(None, title="毛の色", ge=0)
    image_path: Optional[str] = Field(
        None, regex="^[a-z0-9/.]+$", title="画像パス、事前にImageリソースで登録した際に発行されたパス"
    )
    enabled: bool = Field(None, title="有効フラグ")

    def to_model(self, owner_id: str) -> DogModel:
        model = DogModel()
        model.owner_id = owner_id
        model.dog_id = str(uuid.uuid4()).replace("-", "")

        for (key, value) in vars(self).items():
            if key not in model.get_attributes().keys() or not value:
                continue
            setattr(model, key, value)

        return model


class DogResponse(DogRequest):
    id: str = Field(..., title="犬ID")
    updated_at: int = Field(..., title="更新日時(unixtime)")

    @classmethod
    def from_model(cls, model: DogModel) -> "DogResponse":
        response = DogResponse(
            id=model.dog_id,
            name=model.name,
            order=model.order,
            updated_at=model.updated_at,
        )

        for (key, value) in model.attribute_values.items():
            if key not in vars(response).keys() or value == None:  # noqa: E711
                continue
            setattr(response, key, value)
        return response


def dog_id_parameter(
    dog_id: str = Path(..., regex="^[a-z0-9]{32}$", description="犬ID", alias="id"),
):
    return dog_id


@router.get(
    "/",
    response_model=List[DogResponse],
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="犬情報の一覧取得",
    description="オーナーに紐付く犬情報の一覧を取得します",
)
def list(
    owner_id: str = Depends(owner_id_parameter),
) -> List[DogResponse]:
    dogs = [x for x in DogModel.query(hash_key=owner_id)]
    dogs.sort(key=lambda x: x.order)
    for (idx, dog) in enumerate(dogs):
        if idx + 1 == dog.order:
            continue
        dog.order = idx + 1
        dog.save()

    return [DogResponse.from_model(x) for x in dogs]


@router.get(
    "/{id}",
    response_model=DogResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="犬情報の1件取得",
    description="オーナーに紐付く犬情報を1件取得します",
)
def get(
    owner_id: str = Depends(owner_id_parameter), dog_id: str = Depends(dog_id_parameter)
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
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
    summary="犬情報の登録",
    description="オーナーに紐付く犬情報を登録します",
)
def post(
    owner_id: str = Depends(owner_id_parameter),
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
    description="オーナーに紐付く犬情報を更新します",
)
def put(
    owner_id: str = Depends(owner_id_parameter),
    dog_id: str = Depends(dog_id_parameter),
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
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="犬情報の削除",
    description="オーナーに紐付く犬情報を削除します",
)
def delete(
    owner_id: str = Depends(owner_id_parameter),
    dog_id: str = Depends(dog_id_parameter),
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
