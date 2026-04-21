from typing import Annotated, Optional

from pydantic import BaseModel, Field


class InterpretRequest(BaseModel):
    trace_id: Annotated[
        Optional[str],
        Field(description="请求id，追踪请求链路。如果为空，则会生成一个。"),
    ] = None
    conversation_id: Annotated[
        Optional[str],
        Field(
            description="会话id。用户每个会话的 `conversation_id` 应唯一，同一个会话下不同发话（`turn_id`）的 `conversation_id` 应相同。如果为空，则会生成一个。"
        ),
    ] = None
    turn_id: Annotated[
        Optional[str],
        Field(
            description="发话id。用户每次发话 `turn_id` 应唯一，同一次发话下的 `turn_id` 应相同。如果为空，则会生成一个。"
        ),
    ] = None
    policy_content: Annotated[
        Optional[str],
        Field(
            description="政策文件原文。`policy_id` 和 `policy_content` 至少一个不为空，都存在时，优先使用 `policy_content`。"
        ),
    ] = None
    policy_id: Annotated[
        Optional[str] | int,
        Field(
            description="政策文件在数据库中的id。`policy_id` 和 `policy_content` 至少一个不为空，都存在时，优先使用 `policy_content`。"
        ),
    ] = None


class ChatRequest(BaseModel):
    trace_id: Annotated[
        Optional[str],
        Field(description="请求id，追踪请求链路。如果为空，则会生成一个。"),
    ]
    conversation_id: Annotated[
        Optional[str],
        Field(
            description="会话id。用户每个会话的 `conversation_id` 应唯一，同一个会话下不同发话（`turn_id`）的 `conversation_id` 应相同。如果为空，则会生成一个。"
        ),
    ]
    turn_id: Annotated[
        Optional[str],
        Field(
            description="发话id。用户每次发话 `turn_id` 应唯一，同一次发话下的 `turn_id` 应相同。如果为空，则会生成一个。"
        ),
    ]
    question: Annotated[str, Field(description="用户发话。")]
