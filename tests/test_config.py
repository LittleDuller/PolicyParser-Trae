import pytest
from pydantic import SecretStr

from app.core.config import Settings, settings


class TestSettingsDefaults:
    """测试 Settings 类的默认值"""

    def test_db_host_default(self):
        """测试 DB_HOST 默认值为 'localhost'"""
        fresh_settings = Settings()
        assert fresh_settings.DB_HOST == "localhost"

    def test_db_port_default(self):
        """测试 DB_PORT 默认值为 3306"""
        fresh_settings = Settings()
        assert fresh_settings.DB_PORT == 3306

    def test_log_level_default(self):
        """测试 LOG_LEVEL 默认值为 'INFO'"""
        fresh_settings = Settings()
        assert fresh_settings.LOG_LEVEL == "INFO"


class TestDatabaseUrl:
    """测试 database_url 构建"""

    def test_database_url_starts_with(self):
        """测试 database_url 应该以 'mysql+aiomysql://' 开头"""
        test_settings = Settings(
            DB_HOST="localhost",
            DB_PORT=3306,
            DB_USER="root",
            DB_PASSWORD="secret123",
            DB_NAME="test_db",
        )
        assert test_settings.database_url.startswith("mysql+aiomysql://")

    def test_database_url_format(self):
        """测试 database_url 包含正确的格式: user:pass@host:port/dbname?charset=utf8mb4"""
        test_settings = Settings(
            DB_HOST="custom-host",
            DB_PORT=3307,
            DB_USER="test_user",
            DB_PASSWORD="test_pass",
            DB_NAME="test_db",
        )
        expected = "mysql+aiomysql://test_user:test_pass@custom-host:3307/test_db?charset=utf8mb4"
        assert test_settings.database_url == expected

    def test_database_url_empty_password(self):
        """测试空密码时的 database_url 构建"""
        test_settings = Settings(
            DB_HOST="localhost",
            DB_PORT=3306,
            DB_USER="root",
            DB_PASSWORD="",
            DB_NAME="test_db",
        )
        expected = "mysql+aiomysql://root:@localhost:3306/test_db?charset=utf8mb4"
        assert test_settings.database_url == expected


class TestSecretStrSecurity:
    """测试 SecretStr 安全性"""

    def test_db_password_is_secretstr(self):
        """测试 DB_PASSWORD 是 SecretStr 类型"""
        test_settings = Settings(DB_PASSWORD="mysecretpassword")
        assert isinstance(test_settings.DB_PASSWORD, SecretStr)

    def test_db_password_str_masked(self):
        """测试 str(DB_PASSWORD) 显示 '**********' 而非实际密码"""
        test_settings = Settings(DB_PASSWORD="mysecretpassword")
        assert str(test_settings.DB_PASSWORD) == "**********"

    def test_db_password_get_secret_value(self):
        """测试使用 get_secret_value() 才能获取实际值"""
        test_settings = Settings(DB_PASSWORD="mysecretpassword")
        assert test_settings.DB_PASSWORD.get_secret_value() == "mysecretpassword"


class TestEnvironmentVariableOverride:
    """测试环境变量覆盖 (使用 monkeypatch)"""

    def test_db_host_env_override(self, monkeypatch):
        """测试设置 DB_HOST='custom-host'，验证 settings.DB_HOST == 'custom-host'"""
        monkeypatch.setenv("DB_HOST", "custom-host")
        fresh_settings = Settings()
        assert fresh_settings.DB_HOST == "custom-host"

    def test_db_port_env_override(self, monkeypatch):
        """测试 DB_PORT 环境变量覆盖"""
        monkeypatch.setenv("DB_PORT", "5432")
        fresh_settings = Settings()
        assert fresh_settings.DB_PORT == 5432

    def test_db_user_env_override(self, monkeypatch):
        """测试 DB_USER 环境变量覆盖"""
        monkeypatch.setenv("DB_USER", "custom_user")
        fresh_settings = Settings()
        assert fresh_settings.DB_USER == "custom_user"

    def test_multiple_env_override(self, monkeypatch):
        """测试多个环境变量同时覆盖"""
        monkeypatch.setenv("DB_HOST", "prod-host")
        monkeypatch.setenv("DB_PORT", "3308")
        monkeypatch.setenv("DB_USER", "prod_user")
        monkeypatch.setenv("DB_PASSWORD", "prod_password")
        monkeypatch.setenv("DB_NAME", "prod_db")

        fresh_settings = Settings()
        assert fresh_settings.DB_HOST == "prod-host"
        assert fresh_settings.DB_PORT == 3308
        assert fresh_settings.DB_USER == "prod_user"
        assert fresh_settings.DB_PASSWORD.get_secret_value() == "prod_password"
        assert fresh_settings.DB_NAME == "prod_db"


class TestTypeValidation:
    """测试类型验证"""

    def test_db_port_is_int(self):
        """测试 DB_PORT 应该是 int 类型"""
        test_settings = Settings(DB_PORT=3306)
        assert isinstance(test_settings.DB_PORT, int)

    def test_db_echo_is_bool(self):
        """测试 DB_ECHO 应该是 bool 类型"""
        test_settings = Settings(DB_ECHO=True)
        assert isinstance(test_settings.DB_ECHO, bool)

    def test_db_pool_size_is_int(self):
        """测试 DB_POOL_SIZE 应该是 int 类型"""
        test_settings = Settings(DB_POOL_SIZE=10)
        assert isinstance(test_settings.DB_POOL_SIZE, int)

    def test_db_max_overflow_is_int(self):
        """测试 DB_MAX_OVERFLOW 应该是 int 类型"""
        test_settings = Settings(DB_MAX_OVERFLOW=20)
        assert isinstance(test_settings.DB_MAX_OVERFLOW, int)

    def test_db_pool_timeout_is_int(self):
        """测试 DB_POOL_TIMEOUT 应该是 int 类型"""
        test_settings = Settings(DB_POOL_TIMEOUT=60)
        assert isinstance(test_settings.DB_POOL_TIMEOUT, int)

    def test_db_pool_recycle_is_int(self):
        """测试 DB_POOL_RECYCLE 应该是 int 类型"""
        test_settings = Settings(DB_POOL_RECYCLE=7200)
        assert isinstance(test_settings.DB_POOL_RECYCLE, int)


class TestSettingsInstance:
    """测试全局 settings 实例"""

    def test_settings_is_instance_of_settings(self):
        """测试全局 settings 是 Settings 类的实例"""
        assert isinstance(settings, Settings)
