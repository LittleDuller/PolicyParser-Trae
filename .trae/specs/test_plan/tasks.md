# Policy Parser 测试计划 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建测试基础设施与共享 Fixtures
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 更新 `tests/conftest.py`，添加测试共用的 fixtures
  - 添加数据库会话 fixture（异步）
  - 添加测试配置加载 fixture
  - 添加 httpx AsyncClient fixture 用于 API 测试
- **Acceptance Criteria Addressed**: [AC-1, AC-6, AC-7]
- **Test Requirements**:
  - `programmatic` TR-1.1: `db_session` fixture 能够成功获取数据库会话并执行 `SELECT 1`
  - `programmatic` TR-1.2: `client` fixture 能够创建 FastAPI TestClient 或 httpx AsyncClient
  - `programmatic` TR-1.3: 所有 fixture 在测试后正确清理资源
- **Notes**: 参考现有 pytest-asyncio 模式，确保异步 fixture 正确工作

## [x] Task 2: 配置模块单元测试
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 创建 `tests/test_config.py`
  - 测试 `Settings` 类的默认值
  - 测试 `database_url` 属性构建逻辑
  - 测试环境变量覆盖
  - 测试 SecretStr 字段的安全性
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-2.1: 默认 `DB_HOST` 为 `"localhost"`，默认 `DB_PORT` 为 `3306`
  - `programmatic` TR-2.2: `database_url` 格式为 `mysql+aiomysql://...`
  - `programmatic` TR-2.3: `DB_PASSWORD` 作为 SecretStr，在日志/打印时不会泄露
- **Notes**: 使用 `monkeypatch` 或 `pytest-dotenv` 模拟环境变量

## [x] Task 3: 数据库连接集成测试
- **Priority**: P0
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 创建 `tests/test_database.py`
  - 测试连接池初始化
  - 测试会话获取与释放
  - 测试基本查询执行
  - 测试 `get_db_session_context` 上下文管理器
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-3.1: 通过 `get_db_session_context()` 获取会话，执行 `SELECT 1` 返回 `[(1,)]`
  - `programmatic` TR-3.2: 会话在上下文退出后正确关闭
  - `programmatic` TR-3.3: 多个并发会话能够独立工作（可选，简单验证）
- **Notes**: 使用真实数据库连接，不使用 mock

## [x] Task 4: PolicyRepository 数据库请求测试
- **Priority**: P0
- **Depends On**: Task 1, Task 3
- **Description**: 
  - 创建 `tests/test_repository.py`
  - 测试 `get_by_id()` 方法
    - 使用测试 ID: `1`, `1810621833737674803`, `1810621833737674884`
    - 测试不存在的 ID: `999999999999999999`
  - 测试 `get_content_by_id()` 方法
    - 有效 ID 返回非空字符串
    - 无效 ID 抛出 HTTPException(404)
  - 测试 `get_title_by_id()` 方法
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: `get_by_id(1810621833737674803)` 返回非空 PolicyEntity
  - `programmatic` TR-4.2: `get_by_id(999999999999999999)` 返回 `None`
  - `programmatic` TR-4.3: `get_content_by_id()` 对有效 ID 返回 `len(content) > 0` 的字符串
  - `programmatic` TR-4.4: `get_content_by_id()` 对不存在的 ID 抛出 `HTTPException` 且 `status_code == 404`
  - `programmatic` TR-4.5: 三个测试 ID 全部通过查询测试
- **Notes**: 这是核心测试之一，必须使用真实数据库

## [x] Task 5: ClassificationResult 模型格式测试
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 `tests/test_classification_model.py`
  - 测试 `IndustryCategory` 枚举的所有有效值
  - 测试 `ClassificationResult` Pydantic 模型验证
    - 有效枚举值 + 有效置信度 (0.0-1.0) ✓
    - 无效枚举值 → ValidationError
    - 置信度 < 0 → ValidationError
    - 置信度 > 1 → ValidationError
  - 测试 model_dump/json 序列化
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: `IndustryCategory("汽车零部件")` 有效，`IndustryCategory("无效行业")` 抛出 ValueError
  - `programmatic` TR-5.2: `ClassificationResult(category=IndustryCategory.AUTO_PARTS, confidence=0.95)` 验证通过
  - `programmatic` TR-5.3: `confidence=-0.1` 或 `confidence=1.1` 时，Pydantic 抛出 `ValidationError`
  - `programmatic` TR-5.4: `category="无效值"` 时，Pydantic 抛出 `ValidationError`
  - `programmatic` TR-5.5: `model_dump()` 返回包含 `category` (str/enum) 和 `confidence` (float) 的字典
- **Notes**: 纯单元测试，不依赖 LLM 或数据库

## [x] Task 6: 工具函数与边界条件测试
- **Priority**: P1
- **Depends On**: None
- **Description**: 
  - 完善 `tests/test_html_parser.py`（已有基础）
  - 添加边界情况测试:
    - 空 HTML 字符串
    - 纯文本（无 HTML 标签）
    - 特殊字符转义
    - 嵌套标签处理
  - 创建 `tests/test_edge_cases.py` 或整合到相关测试文件
- **Acceptance Criteria Addressed**: [FR-6, FR-8]
- **Test Requirements**:
  - `programmatic` TR-6.1: `html_to_markdown("")` 返回空字符串或不抛异常
  - `programmatic` TR-6.2: `html_to_markdown("纯文本")` 返回 `"纯文本"` 或等价形式
  - `programmatic` TR-6.3: 已有测试继续通过（回归验证）
- **Notes**: 参考现有测试模式扩展

## [x] Task 7: WorkflowRunner 内容解析优先级测试
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 创建 `tests/test_workflow_runner.py`
  - 测试 `_resolve_policy_content()` 方法的优先级逻辑
  - 使用 mock 验证:
    - 当 `policy_content` 存在时，直接使用，不调用数据库
    - 当 `policy_content` 为空但 `policy_id` 存在时，调用数据库
    - 两者都为空时，抛出 400 HTTPException
  - 测试 `policy_id` 格式验证（非数字字符串）
- **Acceptance Criteria Addressed**: [AC-8, FR-8]
- **Test Requirements**:
  - `programmatic` TR-7.1: 提供 `policy_content` 时，`PolicyRepository` 未被实例化/调用（使用 mock 验证）
  - `programmatic` TR-7.2: 只提供 `policy_id="1810621833737674803"` 时，调用数据库并返回内容
  - `programmatic` TR-7.3: `policy_id="无效字符串"` 时，抛出 `HTTPException(400)`
  - `programmatic` TR-7.4: 两者都不提供时，抛出 `HTTPException(400)`
- **Notes**: 需要使用 unittest.mock 或 pytest-mock 进行依赖 mock

## [x] Task 8: API 接口集成测试
- **Priority**: P1
- **Depends On**: Task 1, Task 7
- **Description**: 
  - 创建 `tests/test_api.py`
  - 使用 FastAPI TestClient 或 httpx AsyncClient
  - 测试健康检查接口 `GET /health`
  - 测试分类接口 `POST /api/v1/policy/classify`:
    - 使用 `policy_content` 参数（避免调用 LLM 的测试方式待定，或仅测试请求格式）
    - 测试无效请求体的错误响应
  - 测试请求参数验证
- **Acceptance Criteria Addressed**: [AC-6, FR-4]
- **Test Requirements**:
  - `programmatic` TR-8.1: `GET /health` 返回 `status_code == 200`
  - `programmatic` TR-8.2: 缺少 `policy_content` 和 `policy_id` 的分类请求返回 `400`
  - `programmatic` TR-8.3: 提供有效 `policy_content` 时，请求能够正确路由（注意：实际分类可能需要 mock LLM）
- **Notes**: 对于需要调用 LLM 的接口，考虑只测试请求验证层，或 mock `WorkflowRunner.run_classification`

## [x] Task 9: 测试组织与文档完善
- **Priority**: P2
- **Depends On**: Task 1-8
- **Description**: 
  - 检查并统一测试文件命名规范
  - 确保所有测试可以通过 `pytest` 命令一次运行
  - 检查测试覆盖率（可选，建议）
  - 确保异步测试正确使用 `@pytest.mark.asyncio`
- **Acceptance Criteria Addressed**: [NFR-1, NFR-2]
- **Test Requirements**:
  - `programmatic` TR-9.1: 在项目根目录运行 `pytest` 命令，所有测试通过
  - `programmatic` TR-9.2: 运行 `pytest tests/ -v` 显示清晰的测试执行结果
  - `human-judgement` TR-9.3: 测试文件结构清晰，易于理解和维护
- **Notes**: 最终验证步骤，确保整体测试套件可用
