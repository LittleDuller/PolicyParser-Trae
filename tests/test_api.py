import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.workflow.agents.classification_agent import ClassificationResult, IndustryCategory


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data


@pytest.mark.asyncio
async def test_classify_missing_both_params(client: AsyncClient):
    response = await client.post(
        "/api/v1/policy/classify",
        json={}
    )
    assert response.status_code == 400
    data = response.json()
    assert "policy_content" in data["detail"] or "policy_id" in data["detail"]


@pytest.mark.asyncio
async def test_classify_invalid_policy_id_format(client: AsyncClient):
    response = await client.post(
        "/api/v1/policy/classify",
        json={"policy_id": "invalid-id"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "policy_id" in data["detail"] or "格式" in data["detail"]


@pytest.mark.asyncio
async def test_classify_empty_request_body(client: AsyncClient):
    response = await client.post(
        "/api/v1/policy/classify",
        json={}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_classify_with_only_policy_id_zero(client: AsyncClient):
    response = await client.post(
        "/api/v1/policy/classify",
        json={"policy_id": 0}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_classify_with_valid_content_mock_workflow(client: AsyncClient):
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
async def test_classify_with_valid_policy_id_mock_workflow(client: AsyncClient):
    mock_result = ClassificationResult(
        category=IndustryCategory.BIOMEDICAL,
        confidence=0.85
    )

    with patch(
        'app.api.routes.classification.WorkflowRunner.run_classification',
        new_callable=AsyncMock
    ) as mock_run_classification:
        mock_run_classification.return_value = mock_result

        response = await client.post(
            "/api/v1/policy/classify",
            json={"policy_id": 12345}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "生物医药"
        assert data["confidence"] == 0.85


@pytest.mark.asyncio
async def test_classify_with_conversation_id_and_turn_id(client: AsyncClient):
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
