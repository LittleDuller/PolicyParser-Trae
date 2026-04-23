"""
政策数据访问层
封装对 idsp_policy 表的所有数据库操作
"""

from typing import Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import PolicyEntity


class PolicyRepository:
    """
    政策数据访问 Repository
    提供对 idsp_policy 表的所有 CRUD 操作
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, policy_id: int) -> Optional[PolicyEntity]:
        """
        根据 ID 查询政策记录
        """
        logger.debug("Querying policy by id: {}", policy_id)
        stmt = select(PolicyEntity).where(PolicyEntity.id == policy_id)
        result = await self.session.execute(stmt)
        policy = result.scalar_one_or_none()
        return policy

    async def get_content_by_id(self, policy_id: int) -> str:
        """
        根据 ID 查询政策原文内容
        如果不存在则抛出 404 异常
        """
        policy = await self.get_by_id(policy_id)

        if not policy:
            logger.warning("Policy not found: id={}", policy_id)
            raise HTTPException(
                status_code=404,
                detail=f"未找到 ID={policy_id} 相关的政策文本",
            )

        if not policy.content:
            logger.warning("Policy content is empty: id={}", policy_id)
            raise HTTPException(
                status_code=404,
                detail=f"ID={policy_id} 的政策文本内容为空",
            )

        logger.info("Successfully retrieved policy content: id={}", policy_id)
        return policy.content

    async def get_by_policy_no(self, policy_no: str) -> Optional[PolicyEntity]:
        """
        根据政策编号查询政策记录
        """
        logger.debug("Querying policy by policy_no: {}", policy_no)
        stmt = select(PolicyEntity).where(PolicyEntity.policy_no == policy_no)
        result = await self.session.execute(stmt)
        policy = result.scalar_one_or_none()
        return policy

    async def get_title_by_id(self, policy_id: int) -> Optional[str]:
        """
        根据 ID 查询政策标题
        """
        policy = await self.get_by_id(policy_id)
        return policy.title if policy else None
