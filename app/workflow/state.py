import operator
from typing import Annotated, Optional

from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class PolicyState(BaseModel):
    """
    政策解析与问答的全局状态
    """
    messages: Annotated[list[AnyMessage], operator.add] = Field(default_factory=list)
    policy_content: str  # 政策原文
    interpretation: Optional[str] = None  # 政策解读结果
