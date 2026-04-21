from fastapi import APIRouter

from app.api.routes import chat, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(chat.router, tags=["Policy Chat"])
