import uuid
from datetime import datetime
from typing import List

from app.api.controllers.common import owner_id_parameter
from app.api.controllers.model import EmptyResponse, Message
from app.custom_logging import CustomLogger
from app.models.dog_model import DogModel
from app.models.event_model import EventModel
from app.models.task_model import TaskModel
from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from fastapi.param_functions import Depends
from pydantic import BaseModel
from pydantic.fields import Field

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class EventRequest(BaseModel):
    timestamp: int = Field(..., title="実施日時(unixtime)")
    task_id: str = Field(..., title="タスクID")
    dog_id: str = Field(..., title="犬D")

    def to_model(self, owner_id: str) -> EventModel:
        model = EventModel()
        model.owner_id = owner_id
        model.event_id = str(uuid.uuid4()).replace("-", "")

        for (key, value) in vars(self).items():
            if key not in model.get_attributes().keys() or not value:
                continue
            setattr(model, key, value)

        return model


class EventResponse(EventRequest):
    id: str = Field(..., title="イベントID")
    updated_at: int = Field(..., title="更新日時(unixtime)")

    @classmethod
    def from_model(cls, model: EventModel) -> "EventResponse":
        response = EventResponse(
            id=model.event_id,
            timestamp=model.timestamp,
            task_id=model.task_id,
            dog_id=model.dog_id,
            updated_at=model.updated_at,
        )
        return response


def event_id_parameter(
    event_id: str = Path(..., regex="^[a-z0-9]{32}$", description="イベントID", alias="id"),
):
    return event_id


@router.get(
    "/",
    response_model=List[EventResponse],
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="イベント情報の一覧取得",
    description="オーナーに紐付くイベント情報の一覧を取得します",
)
def list(
    owner_id: str = Depends(owner_id_parameter),
    from_timestamp: int = Query(..., description="実施日時:開始(unixtime)", alias="from"),
    to_timestamp: int = Query(..., description="実施日時:終了(unixtime)", alias="to"),
) -> List[EventResponse]:
    models = EventModel.timestamp_index.query(
        hash_key=owner_id,
        range_key_condition=EventModel.timestamp.between(from_timestamp, to_timestamp),
    )
    return [EventResponse.from_model(x) for x in models]


@router.get(
    "/{id}",
    response_model=EventResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="イベント情報の1件取得",
    description="オーナーに紐付くイベント情報を1件取得します",
)
def get(
    owner_id: str = Depends(owner_id_parameter),
    event_id: str = Depends(event_id_parameter),
) -> EventResponse:

    try:
        return EventResponse.from_model(
            EventModel.get(hash_key=owner_id, range_key=event_id)
        )
    except EventModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="event not found.",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=EventResponse,
    response_model_exclude_unset=True,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
    summary="イベント情報の登録",
    description="オーナーに紐付くイベント情報を登録します",
)
def post(
    owner_id: str = Depends(owner_id_parameter),
    request: EventRequest = Body(...),
) -> EventResponse:
    validate(owner_id, request)
    model = request.to_model(owner_id)
    model.save()
    return EventResponse.from_model(model)


@router.put(
    "/{id}",
    response_model=EventResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="イベント情報の更新",
    description="オーナーに紐付くイベント情報を更新します",
)
def put(
    owner_id: str = Depends(owner_id_parameter),
    event_id: str = Depends(event_id_parameter),
    request: EventRequest = Body(...),
) -> EventResponse:

    try:
        model = EventModel.get(hash_key=owner_id, range_key=event_id)
    except EventModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="event is not exist.",
        )
    validate(owner_id, request)
    for (key, value) in request.dict().items():
        setattr(model, key, value)
    model.updated_at = int(datetime.timestamp(datetime.now()))
    model.save()
    return EventResponse.from_model(model)


@router.delete(
    "/{id}",
    response_model=EmptyResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="イベント情報の削除",
    description="オーナーに紐付くイベント情報を削除します",
)
def delete(
    owner_id: str = Depends(owner_id_parameter),
    event_id: str = Depends(event_id_parameter),
) -> EmptyResponse:

    for model in EventModel.query(
        hash_key=owner_id, range_key_condition=EventModel.event_id == event_id
    ):
        model.delete()
    return EmptyResponse()


def validate(owner_id: str, request: EventRequest) -> None:
    try:
        DogModel.get(hash_key=owner_id, range_key=request.dog_id)
    except DogModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="illegal dog id.",
        )

    try:
        TaskModel.get(hash_key=owner_id, range_key=request.task_id)
    except TaskModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="illegal event id.",
        )
