from app.api.controllers import owner_controller
from fastapi import APIRouter

router = APIRouter()
router.include_router(owner_controller.router, prefix="/owners", tags=["owner"])
