# 金融售前方案辅助编写系统

![coverage](./docs/coverage-badge.svg)

一个基于AI的智能售前方案生成系统,帮助金融行业售前工程师快速生成高质量的售前方案、报价单和投标文档。

## 🎯 系统概述

金融售前方案辅助编写系统是一个专为金融行业设计的智能化售前文档生成平台。系统通过AI技术、知识图谱和模板引擎，帮助售前工程师快速生成专业、高质量的售前方案、技术建议书、报价单和投标文件，显著提升售前工作效率和文档质量。

## ✨ 系统特性

### 核心功能
- 📄 **智能文档管理** - 支持历史方案的上传、解析、分类和智能检索
- 🤖 **AI方案生成** - 基于大语言模型和历史数据自动生成专业方案
- 🎨 **模板引擎** - 灵活的模板管理系统，支持自定义模板和变量
- 📚 **知识库管理** - 产品知识、解决方案、案例库的统一管理
- 📊 **报价单生成** - 智能报价计算和Excel报价单自动生成
- 📤 **多格式导出** - 支持Word、PDF、Excel等多种格式导出

### 技术优势
- 🚀 **高性能** - 基于微服务架构，支持高并发和水平扩展
- 🔒 **企业级安全** - 多层安全防护，符合金融行业安全标准
- 🛡️ **数据保护** - 完整的数据加密和隐私保护机制
- 📊 **实时监控** - 全面的系统监控和性能分析
- 🔧 **易于部署** - 支持Docker容器化部署和Kubernetes编排

## 🏗️ 技术架构

### 系统架构
```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层                                    │
├─────────────────────────────────────────────────────────────────┤
│  React 18 + TypeScript + Ant Design + Vite + Zustand           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      API网关层                                  │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI + JWT认证 + 限流 + 请求验证 + 响应格式化               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      业务服务层                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │  文档服务   │ │  AI生成服务 │ │  用户服务   │              │
│  │  模板服务   │ │  知识库服务 │ │  权限服务   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      数据存储层                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ PostgreSQL  │ │   Redis     │ │Elasticsearch│              │
│  │  (主数据)   │ │  (缓存)     │ │  (搜索)     │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │  ChromaDB   │ │   MinIO     │ │   Qdrant    │              │
│  │(向量存储)   │ │(文件存储)   │ │(向量搜索)   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 核心技术栈

#### 后端技术
- **Python 3.9+** - 现代Python版本，支持异步编程
- **FastAPI** - 高性能异步Web框架，自动API文档
- **SQLAlchemy 2.0** - 现代化ORM，支持异步操作
- **Pydantic** - 数据验证和序列化
- **Alembic** - 数据库迁移工具
- **Celery** - 分布式任务队列
- **Redis** - 缓存和消息队列

#### AI/ML技术
- **LangChain** - AI应用开发框架
- **OpenAI API** - GPT模型接口
- **ChromaDB** - 向量数据库
- **Qdrant** - 高性能向量搜索引擎
- **Transformers** - Hugging Face模型库
- **Sentence-Transformers** - 文本向量化

#### 数据存储
- **PostgreSQL** - 关系型数据库（主数据存储）
- **Redis** - 内存数据库（缓存和会话）
- **Elasticsearch** - 搜索引擎（文档检索）
- **ChromaDB** - 向量数据库（语义搜索）
- **MinIO** - 对象存储（文件存储）
- **Qdrant** - 向量搜索引擎（相似度匹配）

#### 前端技术
- **React 18** - 现代化前端框架
- **TypeScript** - 类型安全的JavaScript
- **Ant Design 5.0** - 企业级UI组件库
- **Vite** - 快速构建工具
- **Zustand** - 轻量级状态管理
- **React Query** - 数据获取和缓存
- **React Router 6** - 路由管理

#### 部署和运维
- **Docker** - 容器化部署
- **Docker Compose** - 本地开发环境
- **Kubernetes** - 生产环境编排
- **Nginx** - 反向代理和负载均衡
- **Prometheus** - 监控指标收集
- **Grafana** - 可视化监控面板
- **ELK Stack** - 日志收集和分析

## 🚀 快速开始

### 📋 前置要求

- **Docker & Docker Compose** - 容器化部署
- **Python 3.9+** - 后端开发环境
- **Node.js 18+** - 前端开发环境
- **Git** - 版本控制

### 🐳 使用Docker Compose（推荐方式）

#### 1. 克隆项目
```bash
git clone <repository-url>
cd Fin_Pre_Assist
```

#### 2. 环境配置
```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑配置文件，设置必要参数
# 至少需要配置数据库连接和AI服务API密钥
vim backend/.env
```

#### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 系统访问
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/v1/docs
- **监控面板**: http://localhost:3001 (Grafana)

### 💻 本地开发环境

#### 后端开发环境

```bash
cd backend

# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 安装项目依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和AI服务

# 数据库初始化
alembic upgrade head

# 启动开发服务器
python app/main.py

# 或使用热重载模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发环境

```bash
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器（热重载）
npm run dev

# 访问前端开发服务器
# http://localhost:5173

# 其他可用命令
npm run build      # 构建生产版本
npm run preview    # 预览构建结果
npm run lint       # 代码检查
npm run test       # 运行测试
```

### 🔧 环境变量配置

#### 基础配置
```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/fin_pre_assist

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 应用配置
SECRET_KEY=your-secret-key-here
APP_ENV=development
DEBUG=true
```

#### AI服务配置
```env
# AI服务提供商 (openai, tongyi, wenxin, ollama)
AI_PROVIDER=openai

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# 通义千问配置
TONGYI_API_KEY=your-tongyi-api-key
TONGYI_MODEL=qwen-turbo

# 本地模型配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### 安全配置
```env
# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# 文件上传配置
MAX_UPLOAD_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md

# 安全配置
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📁 项目结构

```
Fin_Pre_Assist/                          # 项目根目录
├── backend/                             # 后端服务
│   ├── app/                            # 应用代码
│   │   ├── api/                        # API接口层
│   │   │   ├── v1/                     # API版本1
│   │   │   │   ├── auth.py             # 认证接口
│   │   │   │   ├── documents.py        # 文档接口
│   │   │   │   ├── proposals.py        # 方案接口
│   │   │   │   ├── templates.py        # 模板接口
│   │   │   │   └── users.py            # 用户接口
│   │   ├── core/                       # 核心模块
│   │   │   ├── config.py               # 配置管理
│   │   │   ├── database.py             # 数据库连接
│   │   │   ├── security.py             # 安全模块
│   │   │   ├── metrics.py              # 监控指标
│   │   │   └── cache.py                # 缓存配置
│   │   ├── models/                     # 数据模型
│   │   │   ├── user.py                 # 用户模型
│   │   │   ├── document.py             # 文档模型
│   │   │   ├── proposal.py             # 方案模型
│   │   │   ├── template.py             # 模板模型
│   │   │   └── knowledge.py            # 知识库模型
│   │   ├── services/                   # 业务逻辑层
│   │   │   ├── ai_service.py           # AI生成服务
│   │   │   ├── document_service.py     # 文档处理服务
│   │   │   ├── proposal_service.py     # 方案生成服务
│   │   │   ├── template_service.py     # 模板服务
│   │   │   └── user_service.py         # 用户服务
│   │   ├── utils/                      # 工具函数
│   │   │   ├── file_utils.py           # 文件处理工具
│   │   │   ├── ai_utils.py             # AI工具函数
│   │   │   ├── security_utils.py       # 安全工具
│   │   │   └── validation.py           # 验证工具
│   │   └── main.py                     # 应用入口
│   ├── alembic/                        # 数据库迁移
│   ├── tests/                          # 测试代码
│   │   ├── unit/                       # 单元测试
│   │   ├── integration/                # 集成测试
│   │   └── conftest.py                 # 测试配置
│   ├── requirements.txt                # 生产依赖
│   ├── requirements-dev.txt            # 开发依赖
│   ├── Dockerfile                      # 容器镜像
│   ├── pytest.ini                      # 测试配置
│   └── .env.example                    # 环境变量模板
├── frontend/                           # 前端应用
│   ├── src/                            # 源代码
│   │   ├── components/                 # 公共组件
│   │   │   ├── common/                 # 通用组件
│   │   │   ├── document/               # 文档组件
│   │   │   ├── proposal/               # 方案组件
│   │   │   └── template/               # 模板组件
│   │   ├── pages/                      # 页面组件
│   │   │   ├── Dashboard.tsx           # 仪表板
│   │   │   ├── Documents.tsx           # 文档管理
│   │   │   ├── Proposals.tsx           # 方案管理
│   │   │   ├── Templates.tsx           # 模板管理
│   │   │   └── Settings.tsx            # 系统设置
│   │   ├── services/                   # API服务
│   │   │   ├── api.ts                  # API客户端
│   │   │   ├── auth.ts                 # 认证服务
│   │   │   ├── document.ts             # 文档服务
│   │   │   └── proposal.ts             # 方案服务
│   │   ├── store/                      # 状态管理
│   │   │   ├── authStore.ts            # 认证状态
│   │   │   ├── documentStore.ts        # 文档状态
│   │   │   └── proposalStore.ts        # 方案状态
│   │   ├── types/                      # TypeScript类型
│   │   ├── utils/                      # 工具函数
│   │   ├── styles/                     # 样式文件
│   │   └── App.tsx                     # 应用入口
│   ├── public/                         # 静态资源
│   ├── package.json                    # 项目配置
│   ├── vite.config.ts                  # Vite配置
│   ├── tsconfig.json                   # TypeScript配置
│   └── Dockerfile                      # 容器镜像
├── docs/                               # 项目文档
│   ├── 01_产品规划设计/                # 产品规划文档
│   │   ├── 1.1_产品需求规格说明书_PRD.md
│   │   ├── 1.2_系统架构设计文档_SAD.md
│   │   ├── 1.3_数据库设计文档_DBD.md
│   │   └── 1.4_API接口文档.md
│   ├── 02_用户手册/                    # 用户操作手册
│   │   ├── 2.1_用户操作手册.md
│   │   ├── 2.2_管理员手册.md
│   │   └── 2.3_快速参考指南.md
│   ├── 03_部署运维/                    # 部署运维文档
│   │   ├── 3.1_安装部署手册.md
│   │   ├── 3.2_运维手册.md
│   │   └── 3.3_故障排查手册.md
│   ├── 04_安全培训/                    # 安全相关文档
│   │   └── 4.1_安全说明书.md
│   ├── 05_测试开发/                    # 测试开发文档
│   │   └── 5.2_开发者指南.md
│   └── 06_发布管理/                    # 发布管理文档
│       └── 6.1_版本发布说明_v1.2.0.md
├── docker-compose.yml                  # 开发环境编排
├── docker-compose.prod.yml             # 生产环境编排
├── prometheus.yml                      # 监控配置
├── grafana/                            # 监控面板配置
├── nginx/                              # 反向代理配置
├── scripts/                            # 部署脚本
├── tests/                              # 端到端测试
├── .github/                            # GitHub Actions
└── README.md                           # 项目说明
```

## 🔧 核心功能模块

### 1. 智能文档管理
**功能特点：**
- 📤 **多格式支持** - 支持Word、PDF、Excel、PPT、TXT、MD等格式上传
- 🏷️ **智能分类** - 基于AI的内容分析和自动分类
- 🔍 **全文检索** - 支持关键词、语义和向量搜索
- 📋 **版本管理** - 文档版本控制和历史记录
- 👥 **协作功能** - 文档共享、评论和协作编辑

**技术实现：**
- 文档解析：python-docx、PyPDF2、openpyxl
- 文本向量化：sentence-transformers
- 向量存储：ChromaDB + Qdrant
- 搜索引擎：Elasticsearch

### 2. AI方案生成引擎
**核心能力：**
- 🤖 **智能匹配** - 基于历史方案的智能推荐
- ✍️ **自动撰写** - AI自动生成方案各章节内容
- 🎯 **精准定制** - 根据客户需求定制化生成
- 🔄 **迭代优化** - 支持多次迭代和人工优化
- 📊 **报价集成** - 自动生成配套报价单

**生成内容：**
- 📋 执行摘要
- 🎯 项目背景和需求分析
- 🛠️ 解决方案设计
- 📊 技术实施方案
- 💰 项目报价和成本分析
- ⏱️ 实施计划和里程碑
- ✅ 服务保障和支持

### 3. 模板管理系统
**模板类型：**
- 📄 **方案模板** - 各类解决方案标准模板
- 💼 **报价模板** - 不同产品和服务的报价模板
- 📋 **合同模板** - 标准化合同文档模板
- 📊 **PPT模板** - 演示文稿模板

**模板功能：**
- 🔧 **变量定义** - 灵活的模板变量配置
- 📝 **富文本编辑** - 支持复杂格式和图表
- 📊 **动态图表** - 支持数据驱动的图表生成
- 🔗 **版本控制** - 模板版本管理和历史追踪

### 4. 知识库管理
**知识分类：**
- 📦 **产品知识** - 产品功能、特性、优势
- 🛠️ **解决方案** - 行业解决方案和最佳实践
- 📖 **案例库** - 成功案例和客户故事
- 🏭 **行业知识** - 行业趋势、法规政策
- 💡 **技术文档** - 技术规范、实施指南

**智能特性：**
- 🧠 **知识图谱** - 构建领域知识体系
- 🔗 **关联推荐** - 智能推荐相关知识
- 📈 **知识进化** - 基于使用反馈持续优化
- 🎯 **精准搜索** - 多维度知识检索

### 5. 文档导出系统
**支持格式：**
- 📄 **Word文档** - 可编辑的Word格式
- 📋 **PDF文件** - 专业的PDF输出
- 📊 **Excel表格** - 数据报表和报价单
- 🎨 **PPT演示** - 精美的演示文稿
- 🌐 **HTML页面** - 在线展示版本

**导出特性：**
- 🎨 **专业排版** - 符合金融行业标准的排版
- 📊 **图表生成** - 自动插入相关图表和数据
- 🏢 **品牌定制** - 支持企业LOGO和样式定制
- 🔒 **安全控制** - 导出权限和版本控制

## 🤖 AI配置与集成

### 支持的AI服务提供商

系统支持多种主流AI服务，可根据需求灵活切换：

| 提供商 | 模型 | 特点 | 适用场景 |
|--------|------|------|----------|
| **OpenAI** | GPT-3.5/GPT-4 | 通用性强，质量高 | 英文方案、技术文档 |
| **通义千问** | qwen-turbo/qwen-plus | 中文理解好，本土化 | 中文方案、金融文档 |
| **文心一言** | ERNIE-Bot/ERNIE-Bot-4 | 百度生态，中文优化 | 本土化方案 |
| **Ollama** | Llama2/CodeLlama | 本地部署，数据安全 | 私有化部署场景 |

### AI配置示例

#### OpenAI配置
```env
# AI服务提供商
AI_PROVIDER=openai

# OpenAI API配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
```

#### 通义千问配置
```env
# AI服务提供商
AI_PROVIDER=tongyi

# 通义千问API配置
TONGYI_API_KEY=your-tongyi-api-key
TONGYI_MODEL=qwen-turbo
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/api/v1
```

#### 本地模型配置（Ollama）
```env
# AI服务提供商
AI_PROVIDER=ollama

# Ollama本地配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b
OLLAMA_TIMEOUT=300
```

### AI功能调优

#### 生成参数配置
```python
# 方案生成参数
GENERATION_CONFIG = {
    "temperature": 0.7,        # 创造性程度 (0.0-1.0)
    "max_tokens": 4000,        # 最大生成长度
    "top_p": 0.9,             # 核采样参数
    "frequency_penalty": 0.3,  # 频率惩罚
    "presence_penalty": 0.3,   # 存在惩罚
}

# 搜索匹配参数
SEARCH_CONFIG = {
    "similarity_threshold": 0.75,  # 相似度阈值
    "max_results": 10,             # 最大返回结果数
    "rerank_top_k": 5,             # 重排序数量
}
```

#### 提示词工程
系统内置了优化的提示词模板：
- **方案生成提示词** - 引导AI生成结构化方案
- **内容优化提示词** - 提升生成内容质量
- **格式调整提示词** - 确保输出格式规范
- **翻译提示词** - 支持中英文互译

## 🔐 安全特性

### 身份认证与授权
- **JWT Token认证** - 无状态认证机制
- **多因素认证(MFA)** - 增强账户安全性
- **基于角色的访问控制(RBAC)** - 细粒度权限管理
- **单点登录(SSO)** - 支持企业统一认证

### 数据安全保护
- **传输加密** - TLS 1.3端到端加密
- **存储加密** - AES-256数据库加密
- **文件加密** - 文档存储加密
- **敏感数据脱敏** - 自动数据脱敏处理

### 应用安全防护
- **SQL注入防护** - 参数化查询和输入验证
- **XSS攻击防护** - 内容安全策略(CSP)
- **CSRF防护** - 令牌验证机制
- **API限流** - 基于IP和用户的请求限流
- **文件上传安全** - 类型检查和病毒扫描

### 合规性保障
- **GDPR合规** - 欧盟数据保护法规
- **等保三级** - 网络安全等级保护
- **金融行业规范** - 符合金融监管要求
- **审计日志** - 完整的操作审计追踪

## 📊 性能优化

### 后端性能优化
- **数据库优化** - 索引优化、查询优化、连接池
- **缓存策略** - Redis多级缓存、缓存预热
- **异步处理** - Celery异步任务、消息队列
- **API优化** - 响应压缩、分页加载、字段过滤

### 前端性能优化
- **代码分割** - 路由级代码分割
- **懒加载** - 组件和图片懒加载
- **缓存策略** - 浏览器缓存、Service Worker
- **CDN加速** - 静态资源CDN分发

### AI性能优化
- **向量索引** - HNSW近似最近邻搜索
- **模型缓存** - AI响应结果缓存
- **批量处理** - 批量API调用优化
- **流式响应** - 支持流式输出减少等待时间

### 监控指标
- **响应时间** - API平均响应时间 < 500ms
- **并发能力** - 支持1000+并发用户
- **可用性** - 系统可用性 > 99.9%
- **吞吐量** - 文档处理能力 > 1000份/小时

## 🧪 测试体系

### 测试类型
- **单元测试** - 代码覆盖率 > 80%
- **集成测试** - API接口测试
- **端到端测试** - 用户场景测试
- **性能测试** - 负载和压力测试
- **安全测试** - 渗透测试和漏洞扫描

### 测试工具
```bash
# 运行所有测试
cd backend
pytest -v --cov=app --cov-report=html

# 运行特定测试
pytest tests/unit/test_ai_service.py -v

# 性能测试
locust -f tests/locustfile.py --host=http://localhost:8000

# 安全测试
bandit -r app/
safety check
```

## 👨‍💻 开发指南

### 📋 开发环境搭建

#### 1. 环境要求
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose

#### 2. 代码规范

**后端代码规范（Python）**
```python
# 遵循PEP 8规范
# 使用Black进行代码格式化
# 使用isort进行导入排序
# 使用mypy进行类型检查

# 示例代码结构
from typing import Optional
from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    """用户创建请求模型"""
    username: str
    email: str
    password: str
    department: Optional[str] = None

async def create_user(user_data: UserCreateRequest) -> User:
    """创建新用户

    Args:
        user_data: 用户创建请求数据

    Returns:
        User: 创建的用户对象

    Raises:
        ValueError: 用户名已存在
    """
    # 实现逻辑
    pass
```

**前端代码规范（TypeScript/React）**
```typescript
// 使用ESLint + Prettier
// 遵循React Hooks最佳实践
// 使用TypeScript严格模式

// 组件示例
import React, { useState, useEffect } from 'react';
import { Card, Button } from 'antd';

interface DocumentCardProps {
  title: string;
  content: string;
  onEdit: (id: string) => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ title, content, onEdit }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  return (
    <Card title={title} extra={<Button onClick={() => onEdit(title)}>编辑</Button>}>
      <div className={isExpanded ? 'expanded' : 'collapsed'}>{content}</div>
    </Card>
  );
};
```

### 🔧 API开发规范

#### RESTful API设计
```python
# 标准的RESTful API结构
# 使用HTTP动词表示操作
# 使用状态码表示结果

from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """获取文档列表"""
    documents = await document_service.get_user_documents(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return documents

@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    document: DocumentCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """创建新文档"""
    try:
        new_document = await document_service.create_document(
            document_data=document,
            user_id=current_user.id
        )
        return new_document
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### API文档自动化
```python
# FastAPI自动生成交互式API文档
# 访问: http://localhost:8000/api/v1/docs

@router.post("/generate-proposal", response_model=ProposalResponse)
async def generate_proposal(
    request: ProposalGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    生成售前方案

    ## 功能描述
    基于客户需求和历史方案，使用AI技术生成新的售前方案。

    ## 请求参数
    - **customer_requirements**: 客户需求描述
    - **industry**: 客户所属行业
    - **budget_range**: 预算范围
    - **timeline**: 项目时间要求
    - **template_id**: 使用的模板ID

    ## 返回结果
    - **proposal_id**: 生成的方案ID
    - **content**: 方案内容
    - **confidence_score**: AI置信度评分
    - **estimated_time**: 预计完成时间

    ## 使用示例
    ```json
    {
      "customer_requirements": "需要构建一个智能风控系统",
      "industry": "banking",
      "budget_range": "1000000-5000000",
      "timeline": "6个月",
      "template_id": "risk-control-template"
    }
    ```
    """
    # 实现逻辑
    pass
```

### 🎨 前端开发规范

#### 组件设计原则
```typescript
// 1. 单一职责原则
// 2. 可复用性设计
// 3. 类型安全
// 4. 性能优化

// 组件结构示例
import React, { useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Skeleton, Empty } from 'antd';

interface Props {
  documentId: string;
  onUpdate?: (data: Document) => void;
  className?: string;
}

const DocumentEditor: React.FC<Props> = ({ documentId, onUpdate, className }) => {
  // 数据获取
  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => documentService.getDocument(documentId),
    enabled: !!documentId,
  });

  // 事件处理
  const handleUpdate = useCallback((updatedData: Document) => {
    onUpdate?.(updatedData);
  }, [onUpdate]);

  // 渲染优化
  const renderedContent = useMemo(() => {
    if (isLoading) return <Skeleton active />;
    if (error) return <Empty description="加载失败" />;
    if (!document) return <Empty description="文档不存在" />;

    return (
      <div className={className}>
        {/* 编辑器内容 */}
      </div>
    );
  }, [document, isLoading, error, className]);

  return renderedContent;
};
```

### 🗄️ 数据库迁移

使用Alembic进行数据库版本管理：

```bash
cd backend

# 创建新的迁移
alembic revision --autogenerate -m "add user profile table"

# 查看迁移历史
alembic history --verbose

# 升级到最新版本
alembic upgrade head

# 回滚到指定版本
alembic downgrade -1

# 标记当前数据库版本
alembic stamp head
```

### 🧪 测试开发

#### 单元测试
```python
# tests/unit/test_ai_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService

class TestAIService:
    """AI服务单元测试"""

    @pytest.fixture
    def ai_service(self):
        return AIService()

    @pytest.mark.asyncio
    async def test_generate_proposal_success(self, ai_service):
        """测试成功生成方案"""
        # 准备测试数据
        requirements = "需要构建智能风控系统"
        industry = "banking"

        # 执行测试
        result = await ai_service.generate_proposal(
            requirements=requirements,
            industry=industry
        )

        # 验证结果
        assert result is not None
        assert "proposal" in result
        assert "confidence" in result
        assert result["confidence"] > 0.7

    @patch('app.services.ai_service.openai.ChatCompletion.create')
    @pytest.mark.asyncio
    async def test_generate_proposal_with_mock(self, mock_create, ai_service):
        """测试AI服务调用（使用Mock）"""
        # 设置Mock返回值
        mock_create.return_value = Mock(
            choices=[Mock(message=Mock(content="生成的方案内容"))]
        )

        # 执行测试
        result = await ai_service.generate_proposal("测试需求", "test")

        # 验证Mock调用
        mock_create.assert_called_once()
        assert result["proposal"] == "生成的方案内容"
```

#### 集成测试
```python
# tests/integration/test_api_documents.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestDocumentAPI:
    """文档API集成测试"""

    async def test_create_document_flow(self, client: AsyncClient, auth_headers):
        """测试完整文档创建流程"""
        # 1. 上传文档
        with open("tests/fixtures/sample.docx", "rb") as f:
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("sample.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                headers=auth_headers
            )

        assert response.status_code == 201
        document_id = response.json()["id"]

        # 2. 获取文档详情
        response = await client.get(f"/api/v1/documents/{document_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Sample Document"

        # 3. 更新文档
        update_data = {"title": "Updated Title", "tags": ["updated", "test"]}
        response = await client.put(
            f"/api/v1/documents/{document_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

        # 4. 删除文档
        response = await client.delete(f"/api/v1/documents/{document_id}", headers=auth_headers)
        assert response.status_code == 204

        # 5. 验证删除
        response = await client.get(f"/api/v1/documents/{document_id}", headers=auth_headers)
        assert response.status_code == 404
```

## 🚀 部署方案

### 📦 容器化部署

#### 1. Docker Compose部署（推荐）

**开发环境**
```bash
# 使用开发环境配置
docker-compose -f docker-compose.yml up -d

# 包含服务：
# - PostgreSQL (数据库)
# - Redis (缓存)
# - Elasticsearch (搜索)
# - ChromaDB (向量存储)
# - MinIO (对象存储)
# - Backend API (后端服务)
# - Frontend (前端应用)
# - Nginx (反向代理)
```

**生产环境**
```bash
# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d

# 生产环境特性：
# - 多副本部署
# - 负载均衡
# - SSL证书自动配置
# - 监控告警集成
# - 日志集中管理
```

#### 2. Kubernetes部署

**集群架构**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fin-pre-assist
  labels:
    name: fin-pre-assist
```

**核心服务部署**
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: fin-pre-assist
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
    spec:
      containers:
      - name: backend
        image: fin-pre-assist/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### 3. 云服务部署

**AWS部署架构**
```
┌─────────────────────────────────────────────────────────┐
│                    Route 53                             │
│                  (DNS服务)                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 CloudFront                              │
│               (CDN加速)                                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 ALB (应用负载均衡器)                     │
└─────┬───────────────────────────────┬───────────────────┘
     │                               │
┌────▼──────────────┐      ┌─────────▼──────────────┐
│  ECS Fargate       │      │  ECS Fargate           │
│  (后端API)         │      │  (前端应用)            │
└────┬──────────────┘      └─────────┬────────────┘
     │                               │
┌────▼──────────────┐      ┌─────────▼──────────────┐
│  RDS PostgreSQL    │      │  ElastiCache Redis     │
│  (主数据库)        │      │  (缓存服务)            │
└───────────────────┘      └────────────────────────┘
```

**阿里云部署架构**
```
┌─────────────────────────────────────────────────────────┐
│                   云解析DNS                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   CDN加速                                │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  SLB (负载均衡)                          │
└─────┬───────────────────────────────┬───────────────────┘
     │                               │
┌────▼──────────────┐      ┌─────────▼──────────────┐
│  ACK集群           │      │  容器镜像服务ACR        │
│  (容器服务)        │      │  (镜像仓库)            │
└────┬──────────────┘      └────────────────────────┘
     │
┌────▼──────────────┐      ┌────────────────────────┐
│  RDS PostgreSQL    │      │  Redis缓存服务         │
│  (云数据库)        │      │  (内存数据库)          │
└───────────────────┘      └────────────────────────┘
```

### 🔄 持续集成/持续部署 (CI/CD)

#### GitHub Actions工作流
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        pytest -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build backend image
      run: |
        cd backend
        docker build -t fin-pre-assist/backend:${{ github.sha }} .

    - name: Build frontend image
      run: |
        cd frontend
        docker build -t fin-pre-assist/frontend:${{ github.sha }} .

    - name: Push to registry
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push fin-pre-assist/backend:${{ github.sha }}
        docker push fin-pre-assist/frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        # 部署到生产环境的脚本
        ./scripts/deploy-production.sh
```

### 🔧 部署配置

#### 环境配置管理
```bash
# 配置不同环境的参数
├── config/
│   ├── development.env
│   ├── staging.env
│   ├── production.env
│   └── secrets/
│       ├── database-passwords
│       ├── api-keys
│       └── ssl-certificates
```

#### 数据库迁移脚本
```bash
#!/bin/bash
# scripts/migrate-database.sh

echo "开始数据库迁移..."

# 备份当前数据库
echo "备份数据库..."
docker exec postgres pg_dump -U postgres fin_pre_assist > backup_$(date +%Y%m%d_%H%M%S).sql

# 执行数据库迁移
echo "执行迁移..."
docker exec backend alembic upgrade head

# 验证迁移结果
echo "验证迁移结果..."
docker exec backend python -c "from app.core.database import check_db_connection; check_db_connection()"

echo "数据库迁移完成！"
```

### 🏥 健康检查与监控

#### 应用健康检查
```python
# app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import redis

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """系统健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }

    # 检查数据库连接
    try:
        await db.execute("SELECT 1")
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # 检查Redis连接
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status
```

### 📊 监控告警

#### 关键监控指标
- **应用性能**: 响应时间、错误率、吞吐量
- **系统资源**: CPU、内存、磁盘、网络
- **数据库**: 连接数、查询性能、慢查询
- **缓存**: 命中率、内存使用、响应时间
- **业务指标**: 用户活跃度、文档生成量、AI调用成功率

## 🔒 安全特性

### 身份认证与访问控制
- **JWT Token认证** - 无状态认证机制，支持刷新令牌
- **多因素认证(MFA)** - 增强账户安全性，支持TOTP
- **基于角色的访问控制(RBAC)** - 细粒度权限管理
- **单点登录(SSO)** - 支持企业统一认证系统
- **会话管理** - 安全的会话生命周期管理

### 数据安全保护
- **传输加密** - TLS 1.3端到端加密，HSTS安全头
- **存储加密** - AES-256数据库加密，敏感字段加密
- **文件加密** - 文档存储加密，支持客户自有密钥
- **数据脱敏** - 自动数据脱敏处理，符合隐私要求
- **备份加密** - 备份数据加密存储

### 应用安全防护
- **输入验证** - 参数化查询，防止SQL注入
- **XSS防护** - 内容安全策略(CSP)，输出编码
- **CSRF防护** - 令牌验证机制，同源策略
- **API安全** - 请求限流、签名验证、异常检测
- **文件安全** - 类型检查、病毒扫描、大小限制

### 合规性保障
- **GDPR合规** - 欧盟数据保护法规合规
- **等保三级** - 网络安全等级保护三级要求
- **金融行业规范** - 符合金融监管和数据保护要求
- **审计日志** - 完整的操作审计追踪
- **数据主权** - 支持数据本地化存储

### 安全监控
- **实时监控** - 安全事件实时检测
- **异常告警** - 自动安全告警机制
- **威胁情报** - 集成威胁情报源
- **漏洞管理** - 定期漏洞扫描和修复
- **事件响应** - 自动化安全事件响应

## 📊 性能指标与优化

### 系统性能指标
- **响应时间**: API平均响应时间 < 500ms (P95 < 1s)
- **并发能力**: 支持1000+并发用户
- **可用性**: 系统可用性 > 99.9%
- **吞吐量**: 文档处理能力 > 1000份/小时
- **资源利用率**: CPU < 70%, 内存 < 80%

### 性能优化策略

#### 后端优化
- **数据库优化** - 索引优化、查询优化、连接池管理
- **缓存策略** - Redis多级缓存、缓存预热、缓存穿透保护
- **异步处理** - Celery异步任务、消息队列、批量处理
- **API优化** - 响应压缩、分页加载、字段过滤、GraphQL

#### 前端优化
- **代码分割** - 路由级代码分割、动态导入
- **懒加载** - 组件和图片懒加载、虚拟滚动
- **缓存策略** - 浏览器缓存、Service Worker、CDN分发
- **构建优化** - Tree Shaking、代码压缩、资源优化

#### AI性能优化
- **向量索引** - HNSW近似最近邻搜索、IVF索引
- **模型缓存** - AI响应结果缓存、智能预热
- **批量处理** - 批量API调用、并发控制
- **流式响应** - 支持流式输出、减少等待时间

### 监控体系

#### 应用监控
- **Prometheus** - 指标收集和存储
- **Grafana** - 可视化监控面板
- **自定义指标** - 业务指标、性能指标
- **告警规则** - 智能告警和通知

#### 基础设施监控
- **系统资源** - CPU、内存、磁盘、网络
- **服务状态** - 服务健康检查、依赖监控
- **日志分析** - ELK Stack日志收集和分析
- **链路追踪** - 分布式链路追踪

## 🧪 测试体系

### 测试策略
- **单元测试** - 代码覆盖率 > 85%
- **集成测试** - API接口测试、数据库测试
- **端到端测试** - 用户场景测试、UI自动化
- **性能测试** - 负载测试、压力测试、容量测试
- **安全测试** - 渗透测试、漏洞扫描、代码审计

### 测试工具栈
```bash
# 单元测试框架
pytest -v --cov=app --cov-report=html

# API测试
httpx + pytest-asyncio

# 前端测试
jest + react-testing-library

# 性能测试
locust -f tests/locustfile.py --host=http://localhost:8000

# 安全测试
bandit -r app/          # Python安全扫描
safety check             # 依赖安全检查
sqlmap -u target_url     # SQL注入测试
```

### 测试环境
- **开发环境** - 本地开发测试
- **测试环境** - 集成测试环境
- **预生产环境** - 生产环境镜像
- **性能测试环境** - 独立性能测试

## 📚 文档体系

### 文档结构
系统提供了完整的文档体系，涵盖产品规划、开发、部署、运维等各个方面：

```
docs/                               # 文档根目录
├── 01_产品规划设计/                # 产品规划阶段
│   ├── 1.1_产品需求规格说明书_PRD.md  # 产品需求文档
│   ├── 1.2_系统架构设计文档_SAD.md    # 架构设计文档
│   ├── 1.3_数据库设计文档_DBD.md      # 数据库设计
│   └── 1.4_API接口文档.md            # API接口规范
├── 02_用户手册/                    # 用户使用指南
│   ├── 2.1_用户操作手册.md          # 普通用户手册
│   ├── 2.2_管理员手册.md            # 管理员操作手册
│   └── 2.3_快速参考指南.md          # 快速操作指南
├── 03_部署运维/                    # 部署和运维
│   ├── 3.1_安装部署手册.md          # 部署安装指南
│   ├── 3.2_运维手册.md              # 日常运维手册
│   └── 3.3_故障排查手册.md          # 故障处理指南
├── 04_安全培训/                    # 安全相关文档
│   └── 4.1_安全说明书.md            # 安全规范说明
├── 05_测试开发/                    # 测试和开发
│   └── 5.2_开发者指南.md            # 开发规范指南
└── 06_发布管理/                    # 发布管理
    └── 6.1_版本发布说明_v1.2.0.md   # 版本发布说明
```

### 文档特色
- **结构化组织** - 按照软件生命周期阶段组织文档
- **多角色视角** - 针对不同用户角色提供专门文档
- **实战化内容** - 包含大量配置示例和操作步骤
- **持续更新** - 随系统版本更新同步维护

## 🤝 贡献指南

我们欢迎社区贡献，共同推动项目发展！

### 贡献方式
- **🐛 问题报告** - 提交Bug报告和功能建议
- **💡 功能开发** - 参与新功能开发和优化
- **📖 文档完善** - 改进和补充项目文档
- **🧪 测试验证** - 参与测试用例设计和执行
- **🌍 本地化** - 帮助项目多语言本地化

### 开发流程
1. **Fork项目** - 创建个人分支
2. **创建特性分支** - `git checkout -b feature/amazing-feature`
3. **提交更改** - `git commit -m 'Add amazing feature'`
4. **推送分支** - `git push origin feature/amazing-feature`
5. **创建Pull Request** - 提交合并请求

### 代码规范
- 遵循项目的代码规范和风格指南
- 编写清晰的提交信息
- 包含适当的测试用例
- 更新相关文档

## 📝 许可证

本项目基于 [MIT License](LICENSE) 开源协议发布。

### 许可证要点
- **自由使用** - 允许商业和非商业用途
- **修改分发** - 允许修改和再分发
- **版权声明** - 保留原作者版权声明
- **免责声明** - 软件按"现状"提供，无任何担保

## 🆘 技术支持

### 获取帮助
- **📖 文档中心** - 查阅项目文档和FAQ
- **💬 社区论坛** - 参与社区讨论和交流
- **🐛 问题跟踪** - 在GitHub提交Issue
- **📧 邮件支持** - 发送邮件至技术支持团队

### 联系方式
- **项目主页** - [GitHub Repository](https://github.com/your-org/fin-pre-assist)
- **技术文档** - [Documentation Site](https://docs.fin-pre-assist.com)
- **社区论坛** - [Community Forum](https://forum.fin-pre-assist.com)
- **技术支持** - support@fin-pre-assist.com

## 🙏 致谢

感谢所有为项目做出贡献的开发者和用户！

### 特别感谢
- **技术贡献者** - 代码贡献和技术支持
- **文档贡献者** - 文档编写和维护
- **测试贡献者** - 质量保证和测试验证
- **社区用户** - 反馈建议和使用体验

---

## 📌 总结

金融售前方案辅助编写系统是一个专为金融行业设计的智能化文档生成平台，通过AI技术显著提升售前工作效率。系统具有以下核心优势：

### 🎯 核心价值
- **效率提升** - 将方案生成时间从数小时缩短至分钟级
- **质量保障** - AI辅助确保方案内容专业、结构完整
- **知识沉淀** - 构建企业级知识库，实现知识传承
- **标准化输出** - 统一的文档格式和质量标准
- **成本节约** - 减少人工成本，提高资源利用率

### 🚀 技术优势
- **先进的AI技术** - 集成多种大语言模型，支持本地化部署
- **企业级架构** - 微服务架构，支持高并发和水平扩展
- **全面的安全保障** - 多层次安全防护，符合金融行业规范
- **完善的文档体系** - 提供从开发到运维的全套文档
- **开放的生态系统** - 支持二次开发和功能扩展

### 🏆 应用场景
- **售前方案生成** - 快速生成专业的技术方案
- **投标文件编制** - 自动化投标文档生成
- **产品方案定制** - 根据客户需求定制方案
- **知识管理** - 构建企业级知识库系统
- **文档标准化** - 实现文档格式和质量标准化

**金融售前方案辅助系统** - 让售前工作更高效、更专业、更智能！

---

*⭐ 如果这个项目对你有帮助，请给我们一个Star！*

## ❓ 常见问题解答

### 🤖 AI配置相关问题

**Q: 如何配置AI模型？**
A: 在 `backend/.env` 文件中配置相应的API密钥和模型参数。支持OpenAI、通义千问、文心一言等多种AI服务提供商。

**Q: 支持哪些AI模型？**
A: 系统支持GPT-3.5/GPT-4、通义千问、文心一言等主流大语言模型，也支持本地部署的Ollama模型。

**Q: AI生成的内容质量如何？**
A: 系统内置了优化的提示词模板和质量控制机制，生成的内容经过专业调优，符合金融行业文档标准。

**Q: 是否支持本地化AI部署？**
A: 支持，可通过Ollama集成本地部署的开源模型，确保数据安全和隐私保护。

### 📄 文档处理相关问题

**Q: 支持哪些文档格式？**
A: 支持Word(.docx)、PDF、Excel(.xlsx)、PowerPoint(.pptx)、Markdown、文本文件等多种格式。

**Q: 上传文件大小限制？**
A: 默认50MB，可在配置文件中修改 `MAX_UPLOAD_SIZE` 参数，最大支持500MB。

**Q: 如何添加新的文档类型？**
A: 在 `backend/app/services/document_processor.py` 中添加相应的解析器，扩展支持的文档类型。

**Q: 文档内容如何被AI学习？**
A: 上传的文档会自动进行文本提取、向量化存储，用于后续的相似度匹配和内容推荐。

### 🔐 安全和隐私问题

**Q: 系统如何保证数据安全？**
A: 系统采用多层安全防护，包括传输加密、存储加密、访问控制、审计日志等，符合金融行业安全标准。

**Q: 是否支持私有化部署？**
A: 完全支持，可以在企业内网环境中部署，确保数据不出企业边界。

**Q: 如何处理敏感信息？**
A: 系统支持自动数据脱敏、敏感字段加密、访问权限控制等功能，保护敏感信息安全。

**Q: 是否符合GDPR等隐私法规？**
A: 系统设计了完整的隐私保护机制，支持数据主体权利、数据删除、审计追踪等GDPR要求。

### 🚀 部署和运维问题

**Q: 系统部署复杂吗？**
A: 提供了一键部署脚本和Docker Compose配置，5分钟内即可完成基础部署。

**Q: 支持哪些部署方式？**
A: 支持Docker Compose、Kubernetes、云服务部署等多种方式，满足不同规模需求。

**Q: 如何进行系统监控？**
A: 内置了Prometheus + Grafana监控体系，提供实时性能监控和告警功能。

**Q: 系统升级会影响业务吗？**
A: 支持零停机升级，通过滚动更新确保业务连续性。

### 💰 成本和性能问题

**Q: 系统运行成本如何？**
A: 基础版本可运行在单机环境，企业级部署支持按需扩展，有效控制成本。

**Q: 系统性能如何？**
A: 支持1000+并发用户，文档处理能力>1000份/小时，API响应时间<500ms。

**Q: 是否支持高可用部署？**
A: 支持多节点集群部署，提供负载均衡、故障转移等高可用特性。

**Q: 如何优化AI调用成本？**
A: 提供智能缓存、批量处理、模型选择等优化策略，有效降低AI调用成本。

### 🛠️ 开发和定制问题

**Q: 是否支持二次开发？**
A: 完全开源，提供完整的API接口和插件机制，支持深度定制开发。

**Q: 如何集成现有系统？**
A: 提供RESTful API、Webhook、单点登录等多种集成方式，支持与现有系统无缝集成。

**Q: 是否有开发示例？**
A: 提供完整的开发文档、SDK示例和最佳实践指南，帮助快速上手开发。

**Q: 技术支持如何获取？**
A: 提供社区支持、邮件支持、企业级技术支持等多种支持渠道。

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

---

**金融售前方案辅助系统** - 让售前工作更高效！
