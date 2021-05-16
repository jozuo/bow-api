from fastapi import APIRouter

from app.api.controllers import (
    dog_controller,
    event_controller,
    image_controller,
    owner_controller,
    task_controller,
)

router = APIRouter()
router.include_router(
    owner_controller.router,
    prefix="/owners",
    tags=["owner"],
)
router.include_router(
    dog_controller.router,
    prefix="/owners/{owner_id}/dogs",
    tags=["dogs"],
)
router.include_router(
    image_controller.router,
    prefix="/owners/{owner_id}/images",
    tags=["images"],
)
router.include_router(
    task_controller.router,
    prefix="/owners/{owner_id}/tasks",
    tags=["tasks"],
)
router.include_router(
    event_controller.router,
    prefix="/owners/{owner_id}/events",
    tags=["events"],
)
