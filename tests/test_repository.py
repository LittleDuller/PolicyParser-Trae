import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import PolicyEntity
from app.repositories.policy_repository import PolicyRepository


class TestPolicyRepositoryGetById:
    """测试 get_by_id() 方法"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("valid_id", [1, 1810621833737674803, 1810621833737674884])
    async def test_valid_id_returns_policy_entity(self, db_session: AsyncSession, valid_id: int):
        """使用有效 ID 查询，返回非空 PolicyEntity"""
        repo = PolicyRepository(db_session)
        policy = await repo.get_by_id(valid_id)

        assert policy is not None
        assert isinstance(policy, PolicyEntity)

    @pytest.mark.asyncio
    async def test_invalid_id_returns_none(self, db_session: AsyncSession, test_policy_ids: dict):
        """使用无效 ID 查询，返回 None"""
        invalid_id = test_policy_ids["invalid"]
        repo = PolicyRepository(db_session)
        policy = await repo.get_by_id(invalid_id)

        assert policy is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("valid_id", [1, 1810621833737674803, 1810621833737674884])
    async def test_policy_entity_has_required_fields(self, db_session: AsyncSession, valid_id: int):
        """验证返回的 PolicyEntity 有 id 和 content 字段"""
        repo = PolicyRepository(db_session)
        policy = await repo.get_by_id(valid_id)

        assert policy is not None
        assert hasattr(policy, "id")
        assert policy.id == valid_id
        assert hasattr(policy, "content")


class TestPolicyRepositoryGetContentById:
    """测试 get_content_by_id() 方法"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("valid_id", [1, 1810621833737674803, 1810621833737674884])
    async def test_valid_id_returns_non_empty_string(self, db_session: AsyncSession, valid_id: int):
        """使用有效 ID 查询，返回非空字符串"""
        repo = PolicyRepository(db_session)
        content = await repo.get_content_by_id(valid_id)

        assert isinstance(content, str)
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_invalid_id_raises_404_exception(self, db_session: AsyncSession, test_policy_ids: dict):
        """使用无效 ID 查询，抛出 HTTPException(status_code=404)"""
        invalid_id = test_policy_ids["invalid"]
        repo = PolicyRepository(db_session)

        with pytest.raises(HTTPException) as exc_info:
            await repo.get_content_by_id(invalid_id)

        assert exc_info.value.status_code == 404
        assert str(invalid_id) in exc_info.value.detail
        assert "未找到" in exc_info.value.detail
