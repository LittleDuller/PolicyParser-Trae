from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.workflow.agents.classification_agent import ClassificationAgent, ClassificationState
from app.workflow.agents.interpret_agent import InterpretAgent
from app.workflow.state import PolicyState


def route_start(
    state: PolicyState,
) -> Literal["interpretation_node", "qa_node", "__end__"]:
    """
    根据当前状态决定执行哪个节点。
    """
    # 场景1：如果没有解读结果且有传入政策，执行解读
    if not state.interpretation:
        if state.policy_content:
            return "interpretation_node"
        return "__end__"

    # 场景2：已有解读内容，且存在对话消息
    if state.messages:
        # 如果最新的一条消息是用户提问，则进入问答节点
        last_message = state.messages[-1]
        if getattr(last_message, "type", "") == "human":
            return "qa_node"

    # 无后续动作，结束
    return "__end__"


def build_interpret_graph():
    agent = InterpretAgent()
    workflow = StateGraph(PolicyState)

    # 注册节点
    workflow.add_node("interpretation_node", agent.interpretation_node)

    # 设置链路与路由
    workflow.add_edge(START, "interpretation_node")
    workflow.add_edge("interpretation_node", END)

    # 编译图并挂载 MemorySaver 用于隔离请求上下文日志
    memory = MemorySaver()

    graph = workflow.compile(checkpointer=memory)
    return graph


def build_classification_graph():
    agent = ClassificationAgent()
    workflow = StateGraph(ClassificationState)

    # 注册节点
    workflow.add_node("classification_node", agent.classification_node)

    # 设置链路与路由
    workflow.add_edge(START, "classification_node")
    workflow.add_edge("classification_node", END)

    # 编译图并挂载 MemorySaver 用于隔离请求上下文日志
    memory = MemorySaver()

    graph = workflow.compile(checkpointer=memory)
    return graph
