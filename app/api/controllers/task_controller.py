import uuid
from datetime import datetime
from typing import List

from app.api.controllers.common import owner_id_parameter
from app.api.controllers.model import EmptyResponse, Message
from app.custom_logging import CustomLogger
from app.models.task_model import TaskModel
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from pydantic import BaseModel, Field
from starlette.status import HTTP_404_NOT_FOUND

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class TaskRequest(BaseModel):
    icon_no: int = Field(..., title="アイコンNo")
    title: str = Field(..., title="タイトル")
    order: int = Field(..., title="画面表示順", ge=1)
    enabled: bool = Field(None, title="有効フラグ")

    def to_model(self, owner_id: str) -> TaskModel:
        model = TaskModel()
        model.owner_id = owner_id
        model.task_id = str(uuid.uuid4()).replace("-", "")

        for (key, value) in vars(self).items():
            if key not in model.get_attributes().keys() or not value:
                continue
            setattr(model, key, value)

        return model


class TaskResponse(TaskRequest):
    id: str = Field(..., title="タスクID")
    updated_at: int = Field(..., title="更新日時(unixtime)")

    @classmethod
    def from_model(cls, model: TaskModel) -> "TaskResponse":
        response = TaskResponse(
            id=model.task_id,
            icon_no=model.icon_no,
            title=model.title,
            order=model.order,
            enabled=model.enabled,
            updated_at=model.updated_at,
        )

        for (key, value) in model.attribute_values.items():
            if key not in vars(response).keys() or value == None:  # noqa: E711
                continue
            setattr(response, key, value)
        return response


def task_id_parameter(
    task_id: str = Path(..., regex="^[a-z0-9]{32}$", description="タスクID", alias="id"),
):
    return task_id


@router.get(
    "/",
    response_model=List[TaskResponse],
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="タスク情報の一覧取得",
    description="オーナーに紐付くタスク情報の一覧を取得します",
)
def list(
    owner_id: str = Depends(owner_id_parameter),
) -> List[TaskResponse]:
    tasks = [x for x in TaskModel.query(hash_key=owner_id)]
    tasks.sort(key=lambda x: x.order)
    for (idx, task) in enumerate(tasks):
        if idx + 1 == task.order:
            continue
        task.order = idx + 1
        task.save()

    return [TaskResponse.from_model(x) for x in tasks]


@router.get(
    "/{id}",
    response_model=TaskResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="タスク情報の1件取得",
    description="オーナーに紐付くタスク情報を1件取得します",
)
def get(
    owner_id: str = Depends(owner_id_parameter),
    task_id: str = Depends(task_id_parameter),
) -> TaskResponse:
    try:
        return TaskResponse.from_model(
            TaskModel.get(hash_key=owner_id, range_key=task_id)
        )
    except TaskModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found.",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    response_model_exclude_unset=True,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
    summary="タスク情報の登録",
    description="オーナーに紐付くタスク情報を登録します",
)
def post(
    owner_id: str = Depends(owner_id_parameter),
    request: TaskRequest = Body(...),
) -> TaskResponse:
    if is_title_exists(owner_id, request.title):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title is already exists.",
        )

    model = request.to_model(owner_id)
    model.save()
    return TaskResponse.from_model(model)


@router.put(
    "/{id}",
    response_model=TaskResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    summary="タスク情報の更新",
    description="オーナーに紐付くタスク情報を更新します",
)
def put(
    owner_id: str = Depends(owner_id_parameter),
    task_id: str = Depends(task_id_parameter),
    request: TaskRequest = Body(...),
) -> TaskResponse:
    try:
        model = TaskModel.get(hash_key=owner_id, range_key=task_id)
    except TaskModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found.",
        )
    for (key, value) in request.dict().items():
        setattr(model, key, value)
    model.updated_at = int(datetime.timestamp(datetime.now()))
    model.save()
    return TaskResponse.from_model(model)


@router.delete(
    "/{id}",
    response_model=EmptyResponse,
    response_model_exclude_unset=True,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    summary="タスク情報の削除",
    description="オーナーに紐付くタスク情報を削除します",
)
def delete(
    owner_id: str = Depends(owner_id_parameter),
    task_id: str = Depends(task_id_parameter),
) -> EmptyResponse:
    for model in TaskModel.query(
        hash_key=owner_id, range_key_condition=TaskModel.task_id == task_id
    ):
        model.delete()
    return EmptyResponse()


def is_title_exists(owner_id: str, title: str) -> bool:
    for model in TaskModel.query(hash_key=owner_id):
        if model.title == title:
            return True
    return False
