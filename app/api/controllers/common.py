from fastapi import Path, status
from fastapi.exceptions import HTTPException

from app.models.owner_model import OwnerModel


def owner_id_parameter(
    owner_id: str = Path(..., regex="^[a-z0-9]{32}$", description="オーナーID")
):
    try:
        OwnerModel.get(hash_key=owner_id)
    except OwnerModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="owner not found.",
        )
    return owner_id
