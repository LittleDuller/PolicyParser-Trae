import os
from pathlib import PurePath

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_qwq import ChatQwen

from app.workflow.state import PolicyState

environment = Environment(
    loader=FileSystemLoader(PurePath(__file__).parent.parent.joinpath("prompts")),
    enable_async=True
)


class InterpretAgent:
    """政策解析与问答Agent"""

    def __init__(self):
        self.llm = self._get_llm()

    @staticmethod
    def _get_llm() -> ChatQwen:
        """获取本智能体使用的LLM对象。目前使用Qwen，不启用思考模式。"""
        return ChatQwen(
            model=os.getenv("DASHSCOPE_MODEL", "Qwen/Qwen3.5-122B-A10B"),
            extra_body={"enable_thinking": False},
        )

    async def interpretation_node(
        self, state: PolicyState, config: RunnableConfig
    ) -> dict:
        """
        解读节点：政策原文解读。
        """
        template = environment.get_template("interpretation.md.j2")
        prompt = await template.render_async(policy_content=state.policy_content)

        # 调用大模型生成解读
        messages = [HumanMessage(content=prompt)]
        response = await self.llm.ainvoke(messages, config)

        interpretation = response.content
        return {"interpretation": interpretation}

    async def qa_node(self, state: PolicyState, config: RunnableConfig) -> dict:
        """
        问答节点：根据政策原文及解读内容，回答用户的具体问题。
        """
        template = environment.get_template("policy_qa.md.j2")
        system_prompt = await template.render_async(
            policy_content=state.policy_content, interpretation=state.interpretation
        )

        messages = [SystemMessage(content=system_prompt)]
        messages += state.messages

        response = await self.llm.ainvoke(messages, config)

        return {"messages": [response]}
