import uuid

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from app.api.controllers.model import Message
from app.custom_logging import CustomLogger
from app.models.owner_model import OwnerModel

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class OwnerRequest(BaseModel):
    email: EmailStr = Field(..., title="メールアドレス")

    def to_model(self) -> OwnerModel:
        model = OwnerModel()
        model.id = str(uuid.uuid4()).replace("-", "")
        model.email = self.email
        return model


class OwnerResponse(OwnerRequest):
    id: str = Field(..., title="オーナーID")

    @classmethod
    def from_model(cls, model: OwnerModel) -> "OwnerResponse":
        return OwnerResponse(id=model.id, email=model.email)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OwnerResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    summary="オーナー情報の登録",
    description="オーナー情報を登録します",
)
def post(request: OwnerRequest) -> OwnerResponse:
    if is_email_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email is already exists.",
        )

    model = request.to_model()
    model.save()
    return OwnerResponse.from_model(model)


@router.get(
    "/search",
    response_model=OwnerResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
    summary="オーナー情報の検索",
    description="メールアドレスでオーナー情報を検索します",
)
def search(email: EmailStr = Query(..., description="メールアドレス")) -> OwnerResponse:
    for model in OwnerModel.scan(OwnerModel.email == email, limit=1):
        return OwnerResponse.from_model(model)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="owner not found.",
    )


def is_email_exists(email: str) -> bool:
    for model in OwnerModel.scan(OwnerModel.email == email, limit=1):
        return True
    return False
