# 金融售前方案辅助编写系统 - 开发指南

## 项目概述

这是一个基于AI的智能售前方案生成系统，专门帮助金融行业售前工程师快速生成高质量的售前方案、报价单和投标文档。项目采用现代化的全栈架构，使用FastAPI作为后端，React+TypeScript作为前端，并集成了多种AI模型提供商。

## 技术栈

### 后端
- **Python 3.9+**: 主要开发语言
- **FastAPI**: 现代化的Web框架，支持异步处理
- **SQLAlchemy**: ORM框架
- **PostgreSQL**: 主要关系型数据库
- **Redis**: 缓存和会话存储
- **ChromaDB**: 向量数据库，用于语义搜索
- **LangChain**: AI应用框架
- **Alembic**: 数据库迁移工具

### 前端
- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **Ant Design**: UI组件库
- **Vite**: 构建工具
- **Zustand**: 状态管理

### AI提供商支持
- OpenAI (GPT-3.5/GPT-4)
- 通义千问
- 文心一言
- 本地模型（Ollama）

## 项目结构

```
Fin_Pre_Assist/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/           # API路由定义
│   │   ├── core/          # 核心配置（认证、设置、监控）
│   │   ├── models/        # 数据模型定义
│   │   ├── services/      # 业务逻辑服务
│   │   └── main.py        # 应用入口
│   ├── storage/           # 文件存储目录
│   ├── tests/             # 测试文件
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── store/         # Zustand状态管理
│   │   └── App.tsx        # 应用入口
│   ├── package.json       # Node依赖
│   └── Dockerfile
├── alembic/               # 数据库迁移脚本
├── docker-compose.yml     # Docker编排文件
├── .env.example          # 环境变量示例
└── README.md
```

## 核心功能模块

### 1. 文档管理模块
- **文档上传**: 支持Word、PDF、Excel、图片等格式
- **文档解析**: 自动提取文档内容并存储
- **文档向量化**: 将文档内容转换为向量，用于语义搜索
- **文档分类**: 按类型、日期、标签等维度管理

### 2. AI方案生成模块
- **需求分析**: 分析客户输入的需求
- **智能匹配**: 基于向量搜索匹配历史方案
- **内容生成**: 使用AI模型生成方案内容
  - 执行摘要
  - 解决方案概述
  - 技术细节
  - 实施计划
- **方案优化**: 基于历史数据提供优化建议

### 3. 知识库模块
- **产品知识管理**: 存储产品特性、功能说明
- **解决方案库**: 行业解决方案模板
- **案例库**: 成功案例和经验总结
- **语义搜索**: 基于ChromaDB的向量搜索

### 4. 模板管理模块
- **模板创建**: 支持Jinja2模板语法
- **变量定义**: 定义模板中可替换的变量
- **模板预览**: 实时预览模板渲染效果
- **版本管理**: 支持模板版本控制

### 5. 文档导出模块
- **Word导出**: 生成专业的Word文档
- **PDF导出**: 生成PDF格式文档
- **Excel报价**: 生成Excel格式报价单
- **格式自定义**: 支持自定义导出格式

## 架构设计

### 系统架构
```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (React)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │方案管理  │ │需求分析  │ │方案生成  │ │文档导出  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                         HTTPS
                            │
┌─────────────────────────────────────────────────────────┐
│                  API网关层 (FastAPI)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │认证中间件│ │日志中间件│ │限流中间件│ │CORS处理  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────┐
│                     业务逻辑层                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │文档管理  │ │AI引擎    │ │模板引擎  │ │导出服务  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────┐
│                      数据层                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │PostgreSQL│ │ChromaDB  │ │文件存储  │ │Redis缓存 │  │
│  │(结构数据)│ │(向量数据)│ │(文档)    │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
```

### 数据模型
#### 核心实体
- **用户 (User)**: 用户信息、认证、权限
- **文档 (Document)**: 文档信息、内容、元数据
- **方案 (Proposal)**: 售前方案、内容、状态
- **模板 (Template)**: 方案模板、变量、版本
- **知识库条目 (KnowledgeBase)**: 知识、类别、标签

### 缓存策略
- **Redis缓存**: 
  - AI响应缓存 (1小时)
  - 向量搜索结果 (30分钟)
  - 方案列表 (5分钟)
- **自动失效**: 文档/方案变更时自动失效相关缓存

## 开发环境设置

### 前置要求
- Docker & Docker Compose
- Python 3.9+
- Node.js 18+

### 启动开发环境

#### 使用Docker Compose（推荐）
```bash
# 启动所有服务
docker-compose up -d

# 访问系统
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/v1/docs
```

#### 本地开发
```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件
python app/main.py

# 前端开发
cd frontend
npm install
npm run dev
```

## 开发指南

### API开发
- 所有API遵循RESTful规范
- 使用FastAPI框架，支持Pydantic模型验证
- API文档自动生成，访问 `/api/v1/docs`

### 前端开发
- 使用React + TypeScript + Ant Design
- 组件开发规范：
  - 使用函数组件和Hooks
  - TypeScript类型定义
  - 遵循Ant Design设计规范
- 状态管理使用Zustand

### 数据库操作
- 使用SQLAlchemy 2.0+ ORM
- 使用Alembic进行数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "migration message"

# 执行迁移
alembic upgrade head
```

### AI集成
- 支持多种AI提供商
- 在 `backend/.env` 中配置AI参数
- 使用LangChain框架统一管理AI能力

## 测试策略

### 测试层级
- **单元测试**: 测试独立组件和服务 (目标: >80%覆盖率)
- **集成测试**: 测试API端点和数据库交互
- **端到端测试**: 测试完整用户工作流程

### 运行测试
```bash
cd backend

# 运行所有测试
bash run_tests.sh

# 或直接使用pytest
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### CI/CD配置
- GitHub Actions自动执行测试
- 代码覆盖率要求 >70%
- 包含安全扫描 (Bandit, Safety)
- 包含代码格式检查 (Black, Flake8)

## 性能优化

### 缓存优化
- Redis缓存常用查询结果
- AI响应缓存避免重复调用
- 向量搜索结果缓存

### 数据库优化
- 数据库索引优化
- 查询性能分析
- 连接池管理

### 监控指标
- 集成Prometheus监控
- 关键指标: AI调用次数、向量搜索性能、缓存命中率

## 安全性

### 认证授权
- JWT Token认证
- 角色权限控制
- 密码加密存储

### 安全措施
- 输入验证和清理
- XSS防护
- CSRF防护
- SQL注入防护
- 文件上传安全检查
- API请求限流

## 部署

### 生产环境部署
```bash
# 构建Docker镜像
docker-compose build

# 启动服务
docker-compose up -d

# 配置Nginx反向代理（可选）
```

### 环境配置
- 生产环境配置在 `.env.prod`
- 生成强密码和密钥
- 配置SSL证书
- 设置数据库连接池

## 架构亮点

### AI增强功能
- **向量化搜索**: 使用ChromaDB实现语义搜索
- **智能提示词**: 针对金融行业的优化提示词
- **多模型支持**: 支持多个AI提供商

### 完整的文档导出
- **Word文档**: 专业格式，支持章节目录
- **PDF导出**: 高质量PDF格式
- **Excel报价**: 格式化的报价单

### 高性能架构
- **Redis缓存**: 大幅提升响应速度
- **异步处理**: FastAPI异步支持
- **向量搜索**: ChromaDB语义匹配

### 自动化测试
- **高覆盖率**: 目标70%+测试覆盖率
- **多层测试**: 单元、集成、E2E测试
- **安全测试**: XSS/CSRF等多种安全测试
- **性能测试**: k6和Locust性能测试

## 项目状态

### 当前进展
- **功能完整性**: 90%+ (核心功能已完整)
- **测试覆盖率**: 72% (超过70%目标)
- **安全性**: 高 (已完成安全测试)
- **性能**: 优秀 (集成Redis缓存优化)

### 技术债务
- 部分API端点需要进一步优化
- 前端UI组件需要进一步完善
- 错误处理机制可以进一步增强

## 代码规范

### Python代码规范
- 使用Black格式化 (88列宽)
- 使用isort管理导入
- 使用Flake8检查代码质量
- 遵循PEP 8规范

### 前端代码规范
- TypeScript严格模式
- ESLint + Prettier格式检查
- 组件文件名使用PascalCase
- Hook函数使用camelCase

### Git规范
- 使用Conventional Commits
- 提交信息格式: `type(scope): description`
- 例如: `feat(api): add document upload endpoint`

## 常见问题

### Q: 如何添加新的文档类型？
A: 在 `backend/app/services/document_processor.py` 中添加相应的解析器

### Q: 如何切换AI提供商？
A: 在 `backend/.env` 文件中修改 `AI_PROVIDER` 和相关API密钥

### Q: 如何更新数据库模型？
A: 修改models后运行 `alembic revision --autogenerate -m "description"` 和 `alembic upgrade head`

### Q: Redis缓存如何工作？
A: 自动缓存AI响应、向量搜索和方案列表，变更时自动失效