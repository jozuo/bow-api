import uuid

from app.models.owner_model import OwnerModel
from app.api.controllers.model import Message
from app.custom_logging import CustomLogger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()
logger = CustomLogger.getApplicationLogger()


class OwnerRequest(BaseModel):
    email: EmailStr


class OwnerResponse(BaseModel):
    id: str
    email: EmailStr

    @classmethod
    def from_model(cls, model: OwnerModel) -> "OwnerResponse":
        return OwnerResponse(id=model.id, email=model.email)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OwnerResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
)
def post(request: OwnerRequest) -> OwnerResponse:
    if is_email_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email is already exists.",
        )

    model = OwnerModel()
    model.id = str(uuid.uuid4()).replace("-", "")
    model.email = request.email
    model.save()
    return OwnerResponse.from_model(model)


@router.get(
    "/search",
    response_model=OwnerResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": Message}},
)
def search(email: EmailStr) -> OwnerResponse:
    for model in OwnerModel.scan(OwnerModel.email == email, limit=1):
        return OwnerResponse.from_model(model)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="owner is not exist.",
    )


def is_email_exists(email: str) -> bool:
    for item in OwnerModel.scan(OwnerModel.email == email, limit=1):
        return True
    return False
