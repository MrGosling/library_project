from fastapi import APIRouter

from backend.api.v1.routers import v1_router

main_router = APIRouter(prefix='/api')
main_router.include_router(v1_router)
