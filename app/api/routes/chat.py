import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from app.schemas import ChatRequest, InterpretRequest
from app.services.workflow_runner import WorkflowRunner

router = APIRouter()


async def sse_wrapper(
    stream_gen: AsyncGenerator[str, None],
) -> AsyncGenerator[str, None]:
    """包装生成器以符合 SSE (Server-Sent Events) 规范"""
    async for chunk in stream_gen:
        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

@router.post("/api/v1/policy/interpret")
async def parse_policy(req: InterpretRequest):
    """
    提交政策进行异步解析解读。采用 SSE 流式返回。
    """
    logger.info("Starting policy interpret for policy_id={} conversation_id={}", req.policy_id, req.conversation_id)
    generator = WorkflowRunner.generate_parse_stream(req)
    return StreamingResponse(sse_wrapper(generator), media_type="text/event-stream")


@router.post("/api/v1/policy/chat")
async def chat_policy(req: ChatRequest):
    """
    针对已解析的政策继续提问。采用 SSE 流式返回。
    """
    logger.info("Starting policy chat for conversation_id={}", req.conversation_id)
    logger.debug("Chat question: {}", req.question)
    generator = WorkflowRunner.generate_chat_stream(req)
    return StreamingResponse(sse_wrapper(generator), media_type="text/event-stream")
