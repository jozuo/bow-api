from fastapi import APIRouter

from app.api.controllers import dog_controller, image_controller, owner_controller

router = APIRouter()
router.include_router(
    owner_controller.router,
    prefix="/owners",
    tags=["owner"],
)
router.include_router(
    dog_controller.router, prefix="/owners/{owner_id}/dogs", tags=["dogs"]
)
router.include_router(
    image_controller.router, prefix="/owners/{owner_id}/images", tags=["images"]
)
