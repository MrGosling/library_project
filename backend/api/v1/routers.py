from fastapi import APIRouter

from backend.api.v1.endpoints import endpoints_router

v1_router = APIRouter(prefix='/v1')
v1_router.include_router(endpoints_router)
