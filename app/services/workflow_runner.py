import asyncio
from typing import Optional, Union

from fastapi import HTTPException
from langchain_core.messages import HumanMessage
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import ClientDisconnect

from app.repositories import PolicyRepository
from app.schemas.requests import ChatRequest, ClassificationRequest, InterpretRequest
from app.utils import html_to_markdown
from app.workflow.agents.classification_agent import ClassificationResult
from app.workflow.graph import build_classification_graph, build_interpret_graph

graph_app = build_interpret_graph()
classification_graph = build_classification_graph()


class WorkflowRunner:
    @staticmethod
    async def _resolve_policy_content(
        req: Union[InterpretRequest, ClassificationRequest],
        db_session: Optional[AsyncSession] = None,
    ) -> str:
        """
        解析政策内容，遵循优先级：
        1. 如果 policy_content 存在，直接使用（优先级最高）
        2. 如果 policy_id 存在，从数据库查询
        3. 两者都不存在，抛出异常
        """
        if req.policy_content:
            logger.info("Using provided policy_content directly (priority: high)")
            return html_to_markdown(req.policy_content)

        if req.policy_id is not None:
            if not db_session:
                logger.error("policy_id provided but no database session available")
                raise HTTPException(
                    status_code=500,
                    detail="数据库连接未初始化，无法通过 policy_id 查询政策",
                )

            try:
                policy_id = int(req.policy_id)
            except (ValueError, TypeError):
                logger.error("Invalid policy_id format: {}", req.policy_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"policy_id 格式错误: {req.policy_id}",
                )

            logger.info("Querying policy from database by id: {}", policy_id)
            repo = PolicyRepository(db_session)
            content = await repo.get_content_by_id(policy_id)
            return html_to_markdown(content)

        logger.error("Neither policy_content nor policy_id provided")
        raise HTTPException(
            status_code=400,
            detail="policy_content 和 policy_id 至少需要提供一个",
        )

    @staticmethod
    async def generate_parse_stream(
        req: InterpretRequest,
        db_session: Optional[AsyncSession] = None,
    ):
        logger.info("Initializing parse stream for conversation: {}", req.conversation_id)
        config = {"configurable": {"thread_id": req.conversation_id}}

        policy_content = await WorkflowRunner._resolve_policy_content(req, db_session)
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

    @staticmethod
    async def run_classification(
        req: ClassificationRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> ClassificationResult:
        logger.info("Initializing classification for conversation: {}", req.conversation_id)
        config = {"configurable": {"thread_id": req.conversation_id}}

        policy_content = await WorkflowRunner._resolve_policy_content(req, db_session)
        state_input = {"policy_content": policy_content}

        try:
            result = await classification_graph.ainvoke(state_input, config)
            classification_result: ClassificationResult = result["classification"]
            logger.info(
                "Successfully completed classification for conversation: {}, category: {}, confidence: {}",
                req.conversation_id,
                classification_result.category,
                classification_result.confidence
            )
            return classification_result
        except Exception as e:
            logger.exception("Classification failed for conversation {}: {}", req.conversation_id, str(e))
            raise
