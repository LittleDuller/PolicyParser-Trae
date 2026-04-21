from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def check_health():
    """
    检查应用系统健康状态
    """
    return HealthResponse(status="ok", message="Service is running")
