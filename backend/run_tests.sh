#!/bin/bash

echo "=========================================="
echo "金融售前方案辅助系统 - 测试套件"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 创建测试目录
echo -e "\n${YELLOW}准备测试环境...${NC}"
mkdir -p tests
mkdir -p test_reports

# 检查Python和依赖
echo -e "\n${YELLOW}检查Python环境...${NC}"
python --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python未安装！${NC}"
    exit 1
fi

# 安装测试依赖
echo -e "\n${YELLOW}安装测试依赖...${NC}"
pip install pytest pytest-cov pytest-html pytest-asyncio httpx 2>/dev/null || true

# 运行单元测试
echo -e "\n${YELLOW}=========================================="
echo "运行单元测试"
echo -e "==========================================${NC}"
pytest tests/test_vector_service.py tests/test_document_processor.py tests/test_template_service.py tests/test_export_service.py -v --tb=short

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 单元测试通过${NC}"
else
    echo -e "${RED}✗ 单元测试失败${NC}"
fi

# 运行API集成测试
echo -e "\n${YELLOW}=========================================="
echo "运行API集成测试"
echo -e "==========================================${NC}"
pytest tests/test_api_integration.py -v --tb=short

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ API集成测试通过${NC}"
else
    echo -e "${RED}✗ API集成测试失败${NC}"
fi

# 运行所有测试并生成覆盖率报告
echo -e "\n${YELLOW}=========================================="
echo "生成测试覆盖率报告"
echo -e "==========================================${NC}"
pytest tests/ --cov=app --cov-report=html:test_reports/coverage --cov-report=term-missing

# 生成HTML测试报告
echo -e "\n${YELLOW}=========================================="
echo "生成HTML测试报告"
echo -e "==========================================${NC}"
pytest tests/ --html=test_reports/report.html --self-contained-html

echo -e "\n${GREEN}=========================================="
echo "测试完成！"
echo "=========================================="
echo -e "覆盖率报告: test_reports/coverage/index.html"
echo -e "测试报告: test_reports/report.html${NC}"
