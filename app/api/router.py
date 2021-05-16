from fastapi import APIRouter, Security
from fastapi.security.api_key import APIKeyHeader

from app.api.controllers import (
    dog_controller,
    event_controller,
    image_controller,
    owner_controller,
    task_controller,
)

api_key_authorization = Security(
    APIKeyHeader(
        name="x-api-key",
        scheme_name="authorization",
    )
)


router = APIRouter()
router.include_router(
    owner_controller.router,
    prefix="/owners",
    tags=["owner"],
    dependencies=[api_key_authorization],
)
router.include_router(
    dog_controller.router,
    prefix="/owners/{owner_id}/dogs",
    tags=["dogs"],
    dependencies=[api_key_authorization],
)
router.include_router(
    image_controller.router,
    prefix="/owners/{owner_id}/images",
    tags=["images"],
    dependencies=[api_key_authorization],
)
router.include_router(
    task_controller.router,
    prefix="/owners/{owner_id}/tasks",
    tags=["tasks"],
    dependencies=[api_key_authorization],
)
router.include_router(
    event_controller.router,
    prefix="/owners/{owner_id}/events",
    tags=["events"],
    dependencies=[api_key_authorization],
)
