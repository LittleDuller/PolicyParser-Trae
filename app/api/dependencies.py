import uuid
from typing import Annotated, AsyncGenerator, Optional

from fastapi import Header, Response


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


async def get_trace_id(
    response: Response, x_trace_id: Annotated[Optional[str], Header()] = None
):
    x_trace_id = x_trace_id or uuid.uuid4().hex
    response.headers["X-Trace-Id"] = x_trace_id

    return x_trace_id
