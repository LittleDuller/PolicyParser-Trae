import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session_context


@pytest.mark.asyncio
class TestGetDbSessionContext:
    """测试 get_db_session_context 上下文管理器"""

    async def test_get_async_session_successfully(self):
        """测试能够成功获取 AsyncSession"""
        async with get_db_session_context() as session:
            assert session is not None
            assert isinstance(session, AsyncSession)
            assert session.is_active

    async def test_execute_simple_select(self):
        """测试执行简单查询 SELECT 1 返回预期结果"""
        async with get_db_session_context() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    async def test_create_multiple_sessions(self):
        """测试能够创建多个独立会话"""
        async with get_db_session_context() as s1:
            async with get_db_session_context() as s2:
                assert s1 is not s2
