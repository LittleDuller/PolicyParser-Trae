"""
加载环境变量与最佳实践配置
"""

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # 日志配置
    # ==========================
    LOG_LEVEL: str = Field(default="INFO", description="日志输出级别")
    LOG_FORMAT: str = Field(
        default="text",
        description="日志格式模式，支持 'text' (适合本地查看) 或 'json' (适合ELK等日志系统收集)",
    )
    LOG_FILE_PATH: str = Field(default="logs/app.log", description="日志文件保存路径")
    LOG_ROTATION: str = Field(
        default="100 MB",
        description="日志文件轮转条件（大小或是时间，例如 '100 MB' 或 '00:00'）",
    )
    LOG_RETENTION: str = Field(default="30 days", description="日志保留策略")

    # ==========================
    # 监控配置 (LangSmith)
    # ==========================
    LANGSMITH_TRACING: bool = Field(
        default=False, description="是否启用 LangSmith 监控"
    )
    LANGSMITH_API_KEY: Optional[SecretStr] = Field(
        default=None, description="LangSmith API Key"
    )
    LANGSMITH_PROJECT: str = Field(
        default="policy-parser", description="LangSmith 追踪项目名称"
    )

    # ==========================
    # 模型配置 (OpenAI 系列协议)
    # ==========================
    OPENAI_BASE_URL: Optional[str] = Field(
        default=None, description="OpenAI API Base URL"
    )
    OPENAI_API_KEY: Optional[SecretStr] = Field(
        default=None, description="OpenAI API Key，使用 SecretStr 防止日志泄露"
    )
    OPENAI_MODEL: Optional[str] = Field(
        default=None, description="默认使用的 OpenAI 模型"
    )

    # ==========================
    # 模型配置 (DashScope 阿里通义千问)
    # ==========================
    DASHSCOPE_API_BASE: Optional[str] = Field(
        default=None, description="DashScope API Base URL"
    )
    DASHSCOPE_API_KEY: Optional[SecretStr] = Field(
        default=None, description="DashScope API Key"
    )
    DASHSCOPE_MODEL: str = Field(
        default="Qwen/Qwen3.5-122B-A10B", description="默认使用的 DashScope 模型"
    )

    # 配置模型 Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略未在类中定义的额外环境变量，提升安全性
    )


# 实例化单例配置对象，建议全项目统一导入此实例
settings = Settings()
