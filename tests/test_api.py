import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.workflow.agents.classification_agent import ClassificationResult, IndustryCategory


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查接口"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data


@pytest.mark.asyncio
async def test_classify_missing_both_params(client: AsyncClient):
    """测试缺少 policy_content 和 policy_id 时返回 400"""
    response = await client.post(
        "/api/v1/policy/classify",
        json={}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_classify_invalid_policy_id_format(client: AsyncClient):
    """测试 policy_id 格式错误时返回 400"""
    response = await client.post(
        "/api/v1/policy/classify",
        json={"policy_id": "invalid-id"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "policy_id" in data["detail"] or "格式" in data["detail"]


@pytest.mark.asyncio
async def test_classify_with_valid_content_mock_workflow(client: AsyncClient):
    """测试使用 policy_content 时的分类接口（mock WorkflowRunner）"""
    mock_result = ClassificationResult(
        category=IndustryCategory.AUTO_PARTS,
        confidence=0.95
    )

    with patch(
        'app.api.routes.classification.WorkflowRunner.run_classification',
        new_callable=AsyncMock
    ) as mock_run_classification:
        mock_run_classification.return_value = mock_result

        response = await client.post(
            "/api/v1/policy/classify",
            json={"policy_content": "测试政策内容"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "汽车零部件"
        assert data["confidence"] == 0.95


@pytest.mark.asyncio
async def test_classify_with_conversation_id_and_turn_id(client: AsyncClient):
    """测试传入 conversation_id 和 turn_id 可选参数"""
    mock_result = ClassificationResult(
        category=IndustryCategory.HARDWARE_MOLD,
        confidence=0.90
    )

    with patch(
        'app.api.routes.classification.WorkflowRunner.run_classification',
        new_callable=AsyncMock
    ) as mock_run_classification:
        mock_run_classification.return_value = mock_result

        response = await client.post(
            "/api/v1/policy/classify",
            json={
                "policy_content": "测试政策内容",
                "conversation_id": "test-conv-123",
                "turn_id": "test-turn-456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "五金模具"
        assert data["confidence"] == 0.90
