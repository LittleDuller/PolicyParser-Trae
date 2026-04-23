import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.workflow_runner import WorkflowRunner
from app.schemas.requests import ClassificationRequest, InterpretRequest


class TestResolvePolicyContent:
    """测试 WorkflowRunner._resolve_policy_content 方法的优先级逻辑"""

    @pytest.mark.asyncio
    async def test_policy_content_takes_precedence_over_policy_id(self):
        """测试 policy_content 优先于 policy_id"""
        req = ClassificationRequest(
            policy_content="<p>测试内容</p>",
            policy_id="1810621833737674803",
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with patch("app.services.workflow_runner.PolicyRepository") as mock_repo:
            mock_instance = AsyncMock()
            mock_repo.return_value = mock_instance

            result = await WorkflowRunner._resolve_policy_content(req, mock_db_session)

            mock_repo.assert_not_called()
            mock_instance.get_content_by_id.assert_not_called()

        assert "测试内容" in result
        assert "<p>" not in result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "request_class",
        [ClassificationRequest, InterpretRequest],
    )
    async def test_only_policy_content_provided(self, request_class):
        """测试只提供 policy_content，不提供 policy_id"""
        req = request_class(
            policy_content="<div>政策原文内容</div>",
            policy_id=None,
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with patch("app.services.workflow_runner.PolicyRepository") as mock_repo:
            mock_instance = AsyncMock()
            mock_repo.return_value = mock_instance

            result = await WorkflowRunner._resolve_policy_content(req, mock_db_session)

            mock_repo.assert_not_called()
            mock_instance.get_content_by_id.assert_not_called()

        assert "政策原文内容" in result
        assert "<div>" not in result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "policy_id",
        ["1810621833737674803", 1810621833737674803],
    )
    async def test_valid_policy_id_provided(self, policy_id):
        """测试只提供有效 policy_id（支持字符串和整数类型）"""
        req = ClassificationRequest(
            policy_content=None,
            policy_id=policy_id,
        )
        mock_db_session = MagicMock(spec=AsyncSession)
        expected_content = "数据库查询到的政策内容"

        with patch("app.services.workflow_runner.PolicyRepository") as mock_repo:
            mock_instance = AsyncMock()
            mock_instance.get_content_by_id.return_value = f"<p>{expected_content}</p>"
            mock_repo.return_value = mock_instance

            result = await WorkflowRunner._resolve_policy_content(req, mock_db_session)

            mock_repo.assert_called_once_with(mock_db_session)
            mock_instance.get_content_by_id.assert_called_once_with(1810621833737674803)

        assert expected_content in result
        assert "<p>" not in result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_id",
        ["无效字符串", "abc123", "", None],
    )
    async def test_invalid_policy_id_format(self, invalid_id):
        """测试无效 policy_id 格式"""
        req = ClassificationRequest(
            policy_content=None,
            policy_id=invalid_id,
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with pytest.raises(HTTPException) as exc_info:
            await WorkflowRunner._resolve_policy_content(req, mock_db_session)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_neither_provided(self):
        """测试 policy_content 和 policy_id 都不提供"""
        req = ClassificationRequest(
            policy_content=None,
            policy_id=None,
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with pytest.raises(HTTPException) as exc_info:
            await WorkflowRunner._resolve_policy_content(req, mock_db_session)

        assert exc_info.value.status_code == 400
        assert "至少需要提供一个" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_empty_policy_content_with_valid_policy_id(self):
        """测试空 policy_content 但有 policy_id 时使用 policy_id"""
        req = ClassificationRequest(
            policy_content="",
            policy_id="1810621833737674803",
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with patch("app.services.workflow_runner.PolicyRepository") as mock_repo:
            mock_instance = AsyncMock()
            mock_instance.get_content_by_id.return_value = "<p>数据库内容</p>"
            mock_repo.return_value = mock_instance

            await WorkflowRunner._resolve_policy_content(req, mock_db_session)

            mock_repo.assert_called_once_with(mock_db_session)
            mock_instance.get_content_by_id.assert_called_once_with(1810621833737674803)

    @pytest.mark.asyncio
    async def test_whitespace_policy_content(self):
        """测试仅空白字符的 policy_content（被视为有效内容）"""
        req = ClassificationRequest(
            policy_content="   ",
            policy_id="1810621833737674803",
        )
        mock_db_session = MagicMock(spec=AsyncSession)

        with patch("app.services.workflow_runner.PolicyRepository") as mock_repo:
            mock_instance = AsyncMock()
            mock_repo.return_value = mock_instance

            result = await WorkflowRunner._resolve_policy_content(req, mock_db_session)

            mock_repo.assert_not_called()
            mock_instance.get_content_by_id.assert_not_called()

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_policy_id_provided_but_no_db_session(self):
        """测试提供了 policy_id 但没有 db_session"""
        req = ClassificationRequest(
            policy_content=None,
            policy_id="1810621833737674803",
        )

        with pytest.raises(HTTPException) as exc_info:
            await WorkflowRunner._resolve_policy_content(req, db_session=None)

        assert exc_info.value.status_code == 500
        assert "数据库连接未初始化" in exc_info.value.detail
