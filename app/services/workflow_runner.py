import asyncio

from langchain_core.messages import HumanMessage
from loguru import logger
from starlette.requests import ClientDisconnect

from app.schemas.requests import ChatRequest, InterpretRequest
from app.utils import html_to_markdown
from app.workflow.graph import build_interpret_graph

graph_app = build_interpret_graph()


class WorkflowRunner:
    @staticmethod
    async def generate_parse_stream(req: InterpretRequest):
        logger.info("Initializing parse stream for conversation: {}", req.conversation_id)
        config = {"configurable": {"thread_id": req.conversation_id}}

        # 通过模型层从数据库获取真实的原文文本
        # policy_text = await get_policy_content_by_id(db_session, req.policy_id)

        # TODO: 补全查库
        policy_content = ""
        if req.policy_content:
            policy_content = html_to_markdown(req.policy_content)
        state_input = {"policy_content": policy_content}

        try:
            # astream_events 支持捕获模型底层的 Token 推流能力
            async for event in graph_app.astream_events(state_input, config, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
            logger.info("Successfully completed parse stream for conversation: {}", req.conversation_id)
        except asyncio.CancelledError:
            # 捕获 FastAPI 传导过来的协程取消信号
            logger.info("Stream cancelled by client (asyncio) for conversation: {}", req.conversation_id)
            # 可以选择直接 return 结束生成，或者 raise 继续向上抛出交由 FastAPI 处理
            raise
        except ClientDisconnect:
            # 捕获客户端主动断开连接
            logger.info("Stream disconnected by client for conversation: {}", req.conversation_id)
            raise
        except Exception as e:
            logger.exception("Parse stream failed for conversation {}: {}", req.conversation_id, str(e))
            raise

    @staticmethod
    async def generate_chat_stream(req: ChatRequest):
        logger.info("Initializing chat stream for conversation: {}", req.conversation_id)
        config = {"configurable": {"thread_id": req.conversation_id}}
        # 状态持久化机制下，只需传入新的增量消息即可
        state_input = {"messages": [HumanMessage(content=req.question)]}

        try:
            async for event in graph_app.astream_events(state_input, config, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
            logger.info("Successfully completed chat stream for conversation: {}", req.conversation_id)
        except asyncio.CancelledError:
            # 捕获 FastAPI 传导过来的协程取消信号
            logger.info("Stream cancelled by client (asyncio) for conversation: {}", req.conversation_id)
            # 可以选择直接 return 结束生成，或者 raise 继续向上抛出交由 FastAPI 处理
            raise
        except ClientDisconnect:
            # 捕获客户端主动断开连接
            logger.info("Stream disconnected by client for conversation: {}", req.conversation_id)
            raise
        except Exception as e:
            logger.exception("Parse stream failed for conversation {}: {}", req.conversation_id, str(e))
            raise
