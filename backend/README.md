# 后端 (backend) 开发与测试指南

本指南说明后端在本地与CI中的常用开发命令、测试运行方式与工具链。

## 运行依赖

- Python 3.9/3.10（CI同样覆盖）
- pip
- 可选：Redis（缓存集成测试需要），PostgreSQL（生产），测试默认使用 SQLite

## 安装依赖

```bash
cd backend
make install
# 或者
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 常用命令（Makefile）

- `make format` 统一代码风格（black + isort）
- `make lint`   代码检查（flake8）
- `make type`   类型检查（mypy）
- `make test`   运行测试（pytest）
- `make cov`    运行测试并生成覆盖率报告（htmlcov/）
- `make security` 安全扫描（bandit + safety）
- `make dev`    快速开发循环（format + lint + type + test）
- `make ci`     本地模拟CI（lint + type + security + cov）
- `make run`    启动开发服务（FastAPI）

## 测试

默认使用 SQLite 数据库：

```bash
make test
# 或带覆盖率
make cov
# 覆盖率 HTML 报告：backend/htmlcov/index.html
```

如果需要 Redis（部分缓存集成测试）：

- 启动本地Redis（默认 localhost:6379）。
- 或在环境变量中将 `REDIS_HOST` 指向你的Redis服务。

## 环境变量（测试建议）

在CI中使用的示例（可在本地适当导出）：

```bash
DATABASE_URL=sqlite:///./test.db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=test-secret-key-min-32-chars-long-here
CHROMA_PERSIST_DIRECTORY=./storage/chroma
```

## CI 工作流说明（.github/workflows/ci.yml）

- 触发：Push / PR 到 main、develop 分支
- Python 矩阵：3.9 / 3.10
- 步骤：
  1. 安装依赖（含 dev 工具）
  2. Lint（flake8）、格式检查（black --check）
  3. 安全扫描（bandit、safety）
  4. 测试（pytest，SQLite，--cov-fail-under=55）
  5. 类型检查（mypy）
  6. 产物上传（coverage、pytest report、安全报告）

## 运行后端服务（开发）

```bash
make run
# 或
python app/main.py
```

## Alembic（数据库迁移）

首次初始化：

```bash
make alembic-init
```
生成迁移：

```bash
make alembic-rev m=init
```
应用迁移：

```bash
make alembic-upgrade
```

> 注意：迁移前请在 `alembic/env.py` 中配置 `target_metadata`。

## 故障排查

- 依赖安装失败：确认 Python 版本和网络代理；必要时升级 pip。
- 测试失败：查看 `backend/pytest.ini` 与 `tests/` 具体失败信息。
- 覆盖率未达阈值：提升测试或暂时下调 `--cov-fail-under`（CI 中为 55）。
- Redis 连接失败：确认本地 Redis 是否启动，或在环境中禁用相关测试。

---

如需前端构建/联调说明，请查看项目根目录下的 README 与 frontend 目录。
