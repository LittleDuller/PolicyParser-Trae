"""
数据库 ORM 模型定义
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PolicyEntity(Base):
    """
    政策数据表 ORM 模型
    对应数据库表: idsp_policy
    """

    __tablename__ = "idsp_policy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="政策标题")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="政策原文内容")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="政策摘要")
    policy_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="政策编号")
    publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="发布日期")
    publish_org: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="发布机构")
    status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1, comment="状态")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新时间")
