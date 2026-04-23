import os
from enum import Enum
from pathlib import PurePath
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_qwq import ChatQwen
from pydantic import BaseModel, Field

from app.workflow.state import PolicyState

environment = Environment(
    loader=FileSystemLoader(PurePath(__file__).parent.parent.joinpath("prompts")),
    enable_async=True
)


class IndustryCategory(str, Enum):
    AUTO_PARTS = "汽车零部件"
    BIOMEDICAL = "生物医药"
    HARDWARE_MOLD = "五金模具"
    CHEMICAL = "化工"
    OTHER = "其他"


class ClassificationResult(BaseModel):
    category: IndustryCategory = Field(description="政策主要影响的行业分类")
    confidence: float = Field(description="分类置信度，0.0-1.0之间")


class ClassificationState(PolicyState):
    classification: Optional[ClassificationResult] = None


class ClassificationAgent:
    """政策行业分类Agent"""

    def __init__(self):
        self.llm = self._get_llm()

    @staticmethod
    def _get_llm() -> ChatQwen:
        """获取本智能体使用的LLM对象。目前使用Qwen，不启用思考模式。"""
        return ChatQwen(
            model=os.getenv("DASHSCOPE_MODEL", "Qwen/Qwen3.5-122B-A10B"),
            extra_body={"enable_thinking": False, "top_k": 20, "repetition_penalty": 1.0},
            max_tokens=512,
            temperature=0.3,
            top_p=0.8
        )

    async def classification_node(
            self, state: ClassificationState, config: RunnableConfig
    ) -> dict:
        """
        分类节点：根据政策原文进行行业分类。
        """
        template = environment.get_template("classification.md.j2")
        prompt = await template.render_async(policy_content=state.policy_content)

        structured_llm = self.llm.with_structured_output(ClassificationResult)

        messages = [HumanMessage(content=prompt)]
        response = await structured_llm.ainvoke(messages, config)

        return {"classification": response}
