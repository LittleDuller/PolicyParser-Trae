import pytest
from dotenv import load_dotenv

load_dotenv()
from langchain_core.runnables import RunnableConfig

from app.workflow.agents.interpret_agent import InterpretAgent
from app.workflow.state import PolicyState
from tests.utils import get_policy_content_path


@pytest.mark.asyncio
@pytest.mark.parametrize("file_path", get_policy_content_path(pattern='9'))
async def test_interpretation_node(file_path, read_file):
    """测试 InterpretAgent 的政策解析节点 interpretation_node"""
    agent = InterpretAgent()

    policy_content = read_file(file_path)

    # 手动组装 LangGraph 需要的数据状态基类 PolicyState
    mock_state = PolicyState(
        policy_content=policy_content, interpretation=None, messages=[]
    )

    # 触发执行节点
    result = await agent.interpretation_node(state=mock_state, config=RunnableConfig())

    # 标准测试断言
    assert result["interpretation"] is not None
    assert isinstance(result["interpretation"], str)
    assert len(result["interpretation"]) > 0

    print(f"\n====== 解析输出结果 ======\n{result['interpretation']}")
