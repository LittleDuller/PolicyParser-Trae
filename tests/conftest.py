import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session_context
from app.main import app


@pytest.fixture
def read_file():
    def _read_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return _read_file


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """异步数据库会话 fixture"""
    async with get_db_session_context() as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    """异步 HTTP 测试客户端 fixture"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_policy_ids():
    """测试用的政策 ID 列表 fixture"""
    return {
        "valid": [1, 1810621833737674803, 1810621833737674884],
        "invalid": 999999999999999999,
    }
