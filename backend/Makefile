# Makefile - 金融售前方案辅助系统后端
# 使用: make <target>
# 常用: make install / make dev / make test / make lint / make cov / make security

PYTHON := python
PIP := pip
APP_DIR := app
TEST_DIR := tests
COV_FAIL_UNDER := 55

# 如果需要虚拟环境, 可以在执行前 `python -m venv venv && source venv/bin/activate`

.PHONY: help install upgrade freeze format lint type test cov html security bandit safety dev ci clean clean-pyc clean-build run serve alembic-init alembic-rev alembic-upgrade

help:
	@echo "可用目标:"
	@echo "  install          安装运行和开发依赖"
	@echo "  upgrade          升级依赖到最新(谨慎)"
	@echo "  freeze           导出 requirements.txt"
	@echo "  format           使用 black + isort 格式化代码"
	@echo "  lint             flake8 静态检查"
	@echo "  type             mypy 类型检查"
	@echo "  test             运行测试 (不收集覆盖率)"
	@echo "  cov              运行测试并生成覆盖率 (终端+HTML)"
	@echo "  html             仅重新生成 HTML 覆盖率报告"
	@echo "  security         bandit + safety 安全扫描"
	@echo "  dev              开发循环: format + lint + type + test"
	@echo "  ci               CI 本地模拟: lint + type + security + cov"
	@echo "  alembic-init     初始化 Alembic (首次)"
	@echo "  alembic-rev m=msg 自动生成迁移 (示例: make alembic-rev m=add_users)"
	@echo "  alembic-upgrade  应用最新迁移"
	@echo "  run / serve      启动开发服务"
	@echo "  clean            清理缓存与临时文件"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then $(PIP) install -r requirements-dev.txt; fi

upgrade:
	$(PIP) install --upgrade -r requirements.txt || true

freeze:
	$(PIP) freeze > requirements.lock.txt
	@echo "已生成 requirements.lock.txt"

format:
	black $(APP_DIR)/ $(TEST_DIR)/
	isort $(APP_DIR)/ $(TEST_DIR)/

lint:
	flake8 $(APP_DIR)/ --max-line-length=120 --count

type:
	mypy $(APP_DIR)/ --ignore-missing-imports

test:
	pytest $(TEST_DIR)/ -v --maxfail=1

cov:
	pytest $(TEST_DIR)/ -v --cov=$(APP_DIR) --cov-report=term --cov-report=html --cov-fail-under=$(COV_FAIL_UNDER)
	@echo "HTML报告: backend/htmlcov/index.html"

html:
	pytest $(TEST_DIR)/ --cov=$(APP_DIR) --cov-report=html --maxfail=1

security: bandit safety

bandit:
	bandit -r $(APP_DIR)/ -ll -f txt -o bandit-report.txt || true

safety:
	 safety check --output safety-report.txt || true

dev: format lint type test

ci: lint type security cov

run serve:
	$(PYTHON) $(APP_DIR)/main.py

# Alembic 相关
alembic-init:
	alembic init alembic
	@echo "请编辑 alembic/env.py 并配置 target_metadata."

alembic-rev:
	@if [ -z "$(m)" ]; then echo "必须提供迁移描述: make alembic-rev m=add_table"; exit 1; fi
	alembic revision --autogenerate -m "$(m)"

alembic-upgrade:
	alembic upgrade head

clean: clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

clean-build:
	rm -rf htmlcov .pytest_cache dist build *.egg-info

# 结束
