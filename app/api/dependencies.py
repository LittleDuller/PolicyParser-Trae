"""
API 依赖注入
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session as get_db_session_from_core


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库 AsyncSession。
    结合 FastAPI 的 Depends 机制，保证请求结束时关闭连接。
    """
    async for session in get_db_session_from_core():
        yield session
