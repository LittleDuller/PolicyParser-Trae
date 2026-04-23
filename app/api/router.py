from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header

from app.api.routes import chat, classification, health

async def global_trace_header(
    x_trace_id: Annotated[
        Optional[str],
        Header(alias="X-Trace-Id", description="请求链路追踪ID。如果不传，系统会自动生成一个并返回。"),
    ] = None,
):
    pass

api_router = APIRouter(dependencies=[Depends(global_trace_header)])

api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(chat.router, tags=["Policy Chat"])
api_router.include_router(classification.router, tags=["Policy Classification"])
