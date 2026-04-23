from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.schemas import ClassificationRequest
from app.schemas.responses import ClassificationResponse
from app.services.workflow_runner import WorkflowRunner

router = APIRouter()


@router.post(
    "/api/v1/policy/classify",
    response_model=ClassificationResponse,
    responses={
        200: {
            "description": "政策行业分类结果。",
            "content": {
                "application/json": {
                    "example": {
                        "category": "汽车零部件",
                        "confidence": 0.95
                    }
                }
            },
        }
    },
)
async def classify_policy(
    req: ClassificationRequest,
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    对政策文件进行行业分类。返回分类结果和置信度。
    """
    logger.info(
        "Starting policy classification for policy_id={} conversation_id={}",
        req.policy_id,
        req.conversation_id,
    )
    result = await WorkflowRunner.run_classification(req, db_session)
    return ClassificationResponse(
        category=result.category.value,
        confidence=result.confidence
    )
