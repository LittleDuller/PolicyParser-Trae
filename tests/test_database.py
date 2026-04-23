import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session_context, engine, async_session_maker


@pytest.mark.asyncio
class TestGetDbSessionContext:
    """测试 get_db_session_context 上下文管理器"""

    async def test_get_async_session_successfully(self):
        """测试能够成功获取 AsyncSession"""
        async with get_db_session_context() as session:
            assert session is not None
            assert isinstance(session, AsyncSession)
            assert session.is_active

    async def test_session_closed_after_context_exit(self):
        """测试会话在上下文退出后正确关闭/释放"""
        session_ref = None

        async with get_db_session_context() as session:
            session_ref = session
            assert session.is_active

        assert session_ref is not None
        assert not session_ref.is_active

    async def test_execute_simple_select(self):
        """测试执行简单查询 SELECT 1 返回预期结果"""
        async with get_db_session_context() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1


@pytest.mark.asyncio
class TestConnectionPool:
    """测试连接池基本功能"""

    async def test_create_multiple_sessions(self):
        """测试能够创建多个独立会话"""
        session1 = None
        session2 = None

        async with get_db_session_context() as s1:
            session1 = s1
            async with get_db_session_context() as s2:
                session2 = s2
                assert session1 is not session2

    async def test_each_session_can_execute_query(self):
        """测试每个会话都能执行查询"""
        results = []

        async with get_db_session_context() as session1:
            result1 = await session1.execute(text("SELECT 1"))
            results.append(result1.scalar())

        async with get_db_session_context() as session2:
            result2 = await session2.execute(text("SELECT 2"))
            results.append(result2.scalar())

        async with get_db_session_context() as session3:
            result3 = await session3.execute(text("SELECT 3"))
            results.append(result3.scalar())

        assert results == [1, 2, 3]


@pytest.mark.asyncio
class TestTransactionRollback:
    """测试事务回滚"""

    async def test_rollback_on_exception(self):
        """测试在异常情况下会话能够正确回滚"""
        session_ref = None
        exception_raised = False

        try:
            async with get_db_session_context() as session:
                session_ref = session
                await session.execute(text("SELECT 1"))
                raise ValueError("测试异常")
        except ValueError:
            exception_raised = True

        assert exception_raised
        assert session_ref is not None
        assert not session_ref.is_active

    async def test_session_still_usable_after_rollback_scenario(self):
        """测试回滚后，新的会话仍然可用"""
        try:
            async with get_db_session_context() as session:
                raise ValueError("测试异常")
        except ValueError:
            pass

        async with get_db_session_context() as new_session:
            result = await new_session.execute(text("SELECT 42"))
            assert result.scalar() == 42
