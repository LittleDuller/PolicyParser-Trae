# Policy Parser 测试计划 - Product Requirement Document

## Overview

* **Summary**: 为 Policy Parser 系统补充符合工业生产规范的自动化测试套件，涵盖数据库连接、数据库请求、模型生成、API接口等核心模块。

* **Purpose**: 建立可重复、可维护的测试体系，确保系统各组件在变更后仍能正确工作，提升代码质量和部署信心。

* **Target Users**: 开发团队、QA团队、CI/CD系统

## Goals

* 建立完整的单元测试体系，覆盖所有核心模块

* 验证数据库连接池和会话管理的正确性

* 验证数据库CRUD操作（使用指定ID: 1, 1810621833737674803, 1810621833737674884）

* 验证 classify 模型生成的输出格式（无需验证准确性）

* 验证 API 接口的请求/响应契约

* 测试边界条件和异常处理路径

## Non-Goals (Out of Scope)

* 不验证 LLM 输出内容的语义准确性（仅验证格式）

* 不进行性能压力测试（超出单元/集成测试范围）

* 不模拟外部 API 故障（如 DashScope API 不可用）

* 不创建新的生产级功能

## Background & Context

### 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ health.py   │  │ chat.py     │  │ classification.py │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                              │
│              ┌──────────────────────┐                        │
│              │  workflow_runner.py  │                        │
│              └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐    ┌────────────────┐    ┌──────────────────┐
│  Workflow    │    │  Repository    │    │     Utils        │
│  (graph.py)  │    │  (policy_...)  │    │  (html_to_...)   │
└──────────────┘    └────────────────┘    └──────────────────┘
         │                    │
         ▼                    ▼
┌──────────────────┐    ┌────────────────────────────┐
│     Agents       │    │      Database Layer        │
│  classification  │    │  (database.py, entities)   │
│  interpret_agent │    └────────────────────────────┘
└──────────────────┘
```

### 现有测试状态

1. **test\_html\_parser.py**: 测试 HTML 转 Markdown 功能（已存在）
2. **test\_prompt.py**: 测试 InterpretAgent 的 interpretation\_node（已存在，调用真实LLM）
3. **api.py**: 手动 SSE 流测试脚本（非pytest）

### 关键测试数据

* 政策数据库测试ID: `1`, `1810621833737674803`, `1810621833737674884`

## Functional Requirements

### FR-1: 数据库连接测试

* 验证数据库连接池能够正确初始化

* 验证能够获取有效的数据库会话

* 验证连接池参数配置正确生效

* 验证会话的事务管理（commit/rollback）

### FR-2: 数据库请求测试

* 使用指定ID查询政策记录：`1`, `1810621833737674803`, `1810621833737674884`

* 验证 `get_by_id()` 返回正确的 PolicyEntity 或 None

* 验证 `get_content_by_id()` 返回非空字符串或抛出404

* 验证 `get_title_by_id()` 返回正确的标题

* 验证无效ID查询的错误处理

### FR-3: Classify 模型生成格式测试

* 验证 `ClassificationResult` Pydantic 模型结构

* 验证 `IndustryCategory` 枚举值的有效性

* 验证 `confidence` 字段在 0.0-1.0 范围内

* 验证 LLM 结构化输出能够正确解析为 ClassificationResult

### FR-4: API 接口测试

* 验证健康检查接口 `/health` 返回 200

* 验证分类接口 `/api/v1/policy/classify` 的请求/响应格式

* 验证无效请求参数的错误响应

* 验证必要的请求头处理

### FR-5: 配置模块测试

* 验证 Settings 能够正确加载环境变量

* 验证 `database_url` 属性构建正确

* 验证 SecretStr 字段不会泄露敏感信息

### FR-6: 工具函数测试

* 验证 `html_to_markdown()` 正确转换 HTML（已有测试，需完善）

* 测试边界情况：空HTML、特殊字符、嵌套标签

### FR-7: 工作流集成测试

* 验证 `build_classification_graph()` 能正确构建工作流

* 验证 `WorkflowRunner._resolve_policy_content()` 的优先级逻辑

  * policy\_content 优先于 policy\_id

  * 两者都缺失时抛出400错误

### FR-8: 边界条件与异常测试

* 测试无效 policy\_id 格式（非数字字符串）

* 测试不存在的 policy\_id

* 测试空的 policy\_content

* 测试数据库连接失败场景（单元测试中mock）

## Non-Functional Requirements

### NFR-1: 测试独立性

* 每个测试用例相互独立，不依赖其他测试的状态

* 使用适当的 fixture 进行测试隔离

* 集成测试不影响生产数据

### NFR-2: 测试可维护性

* 测试代码遵循 DRY 原则

* 使用描述性的测试函数名

* 测试数据集中管理，便于修改

### NFR-3: 测试可观测性

* 失败的测试提供清晰的断言信息

* 关键测试输出可用于调试

* CI/CD 友好的输出格式

## Constraints

* **技术**: 使用 pytest + pytest-asyncio 进行测试

* **数据库**: 必须连接真实数据库进行集成测试（使用指定测试ID）

* **LLM**: 分类测试仅验证输出格式，不调用真实API或使用mock

* **环境**: 测试需要 .env 文件中的数据库配置

## Assumptions

* 测试数据库中存在 ID 为 `1`, `1810621833737674803`, `1810621833737674884` 的记录

* 开发环境已配置正确的数据库连接信息

* 测试不会修改生产数据（仅读取操作）

* pytest 版本 >= 9.0.3，pytest-asyncio >= 1.3.0

## Acceptance Criteria

### AC-1: 数据库连接验证

* **Given**: 配置了正确的数据库连接信息

* **When**: 尝试获取数据库会话

* **Then**: 能够成功创建会话并执行简单查询

* **Verification**: `programmatic`

* **Notes**: 使用 `SELECT 1` 验证连接有效性

### AC-2: 数据库查询验证 - 有效ID

* **Given**: 数据库中存在 ID 为 `1810621833737674803` 的政策记录

* **When**: 调用 `get_by_id(1810621833737674803)`

* **Then**: 返回非空的 PolicyEntity 对象，包含 content 字段

* **Verification**: `programmatic`

### AC-3: 数据库查询验证 - 无效ID

* **Given**: 数据库中不存在 ID 为 `999999999999999999` 的记录

* **When**: 调用 `get_by_id(999999999999999999)`

* **Then**: 返回 `None`

* **Verification**: `programmatic`

### AC-4: ClassificationResult 格式验证

* **Given**: 一个包含有效枚举值和置信度的字典

* **When**: 使用该字典创建 `ClassificationResult` 实例

* **Then**:

  * `category` 必须是有效的 `IndustryCategory` 枚举值

  * `confidence` 必须在 `0.0 <= confidence <= 1.0` 范围内

* **Verification**: `programmatic`

### AC-5: ClassificationResult 边界值测试

* **Given**:

  * 场景A: `confidence = -0.1` (小于0)

  * 场景B: `confidence = 1.1` (大于1)

  * 场景C: `category = "无效行业"` (非枚举值)

* **When**: 尝试创建 `ClassificationResult` 实例

* **Then**: Pydantic 验证失败，抛出 `ValidationError`

* **Verification**: `programmatic`

### AC-6: API 健康检查

* **Given**: 应用服务已启动

* **When**: 发送 GET 请求到 `/health`

* **Then**: 返回 HTTP 200 状态码

* **Verification**: `programmatic`

### AC-7: 配置加载验证

* **Given**: 环境变量中设置了 `DB_HOST=localhost`, `DB_PORT=3306`

* **When**: 实例化 `Settings` 对象

* **Then**:

  * `settings.DB_HOST` == `"localhost"`

  * `settings.DB_PORT` == `3306`

  * `database_url` 包含正确的连接字符串格式

* **Verification**: `programmatic`

### AC-8: 政策内容解析优先级

* **Given**: 请求同时包含 `policy_content` 和 `policy_id`

* **When**: 调用 `_resolve_policy_content()`

* **Then**: 优先使用 `policy_content`，不查询数据库

* **Verification**: `programmatic`

* **Notes**: 通过 mock 验证数据库查询未被调用

## Open Questions

* [ ] 是否需要为测试创建专用的数据库测试环境？（当前假设使用现有数据库的只读测试）

* [ ] 是否需要测试 SSE 流式输出的正确性？（interpret 接口）

* [ ] 是否需要添加代码覆盖率要求？（如 80% 覆盖率）

* [ ] 是否需要在 CI/CD 中自动运行这些测试？

