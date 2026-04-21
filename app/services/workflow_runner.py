from langchain_core.messages import HumanMessage
from markdownify import markdownify as md

from app.schemas.requests import ChatRequest, InterpretRequest
from app.workflow.graph import build_interpret_graph

graph_app = build_interpret_graph()


class WorkflowRunner:
    @staticmethod
    async def generate_parse_stream(req: InterpretRequest):
        config = {"configurable": {"thread_id": req.conversation_id}}

        # 通过模型层从数据库获取真实的原文文本
        # policy_text = await get_policy_content_by_id(db_session, req.policy_id)

        # TODO: 补全查库
        if req.policy_content:
            policy_content = md(req.policy_content)
        state_input = {"policy_content": policy_content}

        # astream_events 支持捕获模型底层的 Token 推流能力
        async for event in graph_app.astream_events(state_input, config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content

    @staticmethod
    async def generate_chat_stream(req: ChatRequest):
        config = {"configurable": {"thread_id": req.conversation_id}}
        # 状态持久化机制下，只需传入新的增量消息即可
        state_input = {"messages": [HumanMessage(content=req.question)]}

        async for event in graph_app.astream_events(state_input, config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content
