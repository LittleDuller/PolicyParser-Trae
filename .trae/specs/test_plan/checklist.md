# Policy Parser 测试验证清单

## 基础设施与 Fixtures
- [x] 数据库会话 fixture 能够成功连接数据库并执行 `SELECT 1`
- [x] httpx/FastAPI 测试客户端 fixture 可用
- [x] 所有异步 fixture 正确使用 `pytest-asyncio` 模式
- [x] 测试环境变量正确加载（数据库配置等）

## 配置模块测试
- [x] `Settings` 类默认值测试通过
- [x] `database_url` 属性构建格式正确
- [x] `SecretStr` 字段不会在日志/打印时泄露密码
- [x] 环境变量覆盖测试通过（使用 monkeypatch）

## 数据库连接测试
- [x] `get_db_session_context()` 上下文管理器能够获取有效会话
- [x] 会话在上下文退出后正确关闭/释放
- [x] 基本查询（如 `SELECT 1`）执行成功

## 数据库请求测试 (核心)
- [x] 测试 ID `1` 查询成功
- [x] 测试 ID `1810621833737674803` 查询成功
- [x] 测试 ID `1810621833737674884` 查询成功
- [x] 不存在的 ID `999999999999999999` 查询返回 `None`
- [x] `get_content_by_id()` 对有效 ID 返回非空字符串
- [x] `get_content_by_id()` 对不存在 ID 抛出 `HTTPException(404)`
- [x] `PolicyEntity` ORM 模型字段映射正确

## ClassificationResult 模型格式测试 (核心)
- [x] `IndustryCategory` 枚举所有 5 个值验证有效
- [x] 无效枚举值抛出 `ValueError` 或 `ValidationError`
- [x] `ClassificationResult(category=..., confidence=0.5)` 验证通过
- [x] `confidence=-0.1` 触发 `ValidationError`
- [x] `confidence=1.1` 触发 `ValidationError`
- [x] `model_dump()` 输出包含 `category` 和 `confidence` 字段
- [x] `confidence` 字段类型为 `float`

## 工具函数测试
- [x] 现有 `test_html_parser.py` 测试全部通过
- [x] 空 HTML 输入处理正确（不抛异常）
- [x] 纯文本输入正确保留
- [x] 特殊字符转义处理正确

## WorkflowRunner 优先级测试
- [x] 同时提供 `policy_content` 和 `policy_id` 时，优先使用 `policy_content`
- [x] 只提供 `policy_content` 时，不调用数据库（mock 验证）
- [x] 只提供有效 `policy_id` 时，正确查询数据库
- [x] `policy_id` 为非数字字符串时，抛出 `HTTPException(400)`
- [x] 两者都不提供时，抛出 `HTTPException(400)`

## API 接口测试
- [x] `GET /health` 返回 200 状态码
- [x] 分类接口缺少必要参数时返回 400
- [x] 请求体验证正确工作（Pydantic 验证）
- [x] 错误响应格式符合预期

## 整体验证
- [x] 运行 `pytest` 命令，所有测试通过
- [x] 运行 `pytest -v` 显示清晰的测试执行情况
- [x] 测试代码风格与现有代码一致
- [x] 没有测试相互依赖（独立性）
- [x] 测试没有修改生产数据（仅读取操作）

## 关键回归检查
- [x] 现有 `test_html_parser.py` 继续通过
- [x] 现有 `test_prompt.py` 继续通过（如适用）
