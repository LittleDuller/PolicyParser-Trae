from typing import AsyncGenerator


async def get_db_session() -> AsyncGenerator:
    """
    获取数据库 AsyncSession。
    结合 FastAPI 的 Depends 机制，保证请求结束时关闭连接。
    """
    # TODO: 替换为具体的 SQLAlchemy async_sessionmaker().begin()
    session = "fake_async_session"
    try:
        yield session
    finally:
        pass
        # await session.close()
