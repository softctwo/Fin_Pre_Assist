# 金融售前方案辅助编写系统

![coverage](./docs/coverage-badge.svg)

一个基于AI的智能售前方案生成系统,帮助金融行业售前工程师快速生成高质量的售前方案、报价单和投标文档。

## 系统特性

- 📄 **文档管理** - 上传和管理历史方案、报价单、投标文档
- 🤖 **智能生成** - 基于AI技术和历史数据自动生成新方案
- 🎨 **模板系统** - 灵活的模板管理，支持自定义
- 📚 **知识库** - 产品知识、解决方案、案例库管理
- 📤 **文档导出** - 支持导出Word、PDF等格式

## 技术栈

### 后端
- Python 3.9+
- FastAPI - 现代化的Web框架
- SQLAlchemy - ORM
- PostgreSQL - 关系型数据库
- ChromaDB - 向量数据库
- LangChain - AI应用框架

### 前端
- React 18
- TypeScript
- Ant Design - UI组件库
- Vite - 构建工具
- Zustand - 状态管理

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+

### 使用Docker Compose（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd Fin_Pre_Assist
```

2. 配置环境变量
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件，配置必要的参数
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 访问系统
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/v1/docs

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动开发服务器
python app/main.py
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
Fin_Pre_Assist/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 应用入口
│   ├── storage/           # 文件存储
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API服务
│   │   ├── store/         # 状态管理
│   │   └── App.tsx        # 应用入口
│   ├── package.json       # Node依赖
│   └── Dockerfile
├── docker-compose.yml     # Docker编排
└── README.md
```

## 功能模块

### 1. 文档管理
- 上传历史方案文档（Word、PDF、Excel）
- 文档分类和标签管理
- 文档内容提取和索引
- 文档检索和预览

### 2. 方案生成
- 输入客户需求
- 智能匹配历史方案
- AI自动生成方案内容
  - 执行摘要
  - 解决方案概述
  - 技术细节
  - 实施计划
- 方案编辑和优化

### 3. 模板管理
- 创建和编辑方案模板
- 模板变量定义
- 模板版本管理

### 4. 知识库
- 产品知识管理
- 解决方案库
- 案例库
- 行业知识

### 5. 文档导出
- 导出为Word文档
- 导出为PDF
- 生成Excel报价单

## AI配置

系统支持多种AI提供商：

- OpenAI (GPT-3.5/GPT-4)
- 通义千问
- 文心一言
- 本地模型（Ollama）

在 `backend/.env` 文件中配置：

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key
```

## 开发指南

### API开发

所有API遵循RESTful规范，使用FastAPI框架开发。

API文档自动生成，访问 `/api/v1/docs` 查看。

### 前端开发

使用React + TypeScript + Ant Design开发。

组件开发规范：
- 使用函数组件和Hooks
- TypeScript类型定义
- 遵循Ant Design设计规范

### 数据库迁移

使用Alembic进行数据库迁移：

```bash
cd backend

# 创建迁移
alembic revision --autogenerate -m "migration message"

# 执行迁移
alembic upgrade head
```

## 部署

### 生产环境部署

1. 构建Docker镜像
```bash
docker-compose build
```

2. 启动服务
```bash
docker-compose up -d
```

3. 配置Nginx反向代理（可选）

## 安全性

- JWT Token认证
- 密码加密存储
- API请求限流
- 文件类型检查
- SQL注入防护

## 性能优化

- Redis缓存
- 数据库索引优化
- API响应压缩
- 静态资源CDN

## 常见问题

### Q: 如何配置AI模型？
A: 在 `backend/.env` 文件中配置相应的API密钥和模型参数。

### Q: 上传文件大小限制？
A: 默认50MB，可在配置文件中修改 `MAX_UPLOAD_SIZE` 参数。

### Q: 如何添加新的文档类型？
A: 在 `backend/app/services/document_processor.py` 中添加相应的解析器。

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

---

**金融售前方案辅助系统** - 让售前工作更高效！
