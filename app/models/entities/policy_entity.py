"""
数据库 ORM 模型定义
"""

from typing import Optional

from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PolicyEntity(Base):
    """
    政策数据表 ORM 模型
    对应数据库表: idsp_policy
    仅映射当前需要的字段，避免列名不匹配问题
    """

    __tablename__ = "idsp_policy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="政策原文内容")
