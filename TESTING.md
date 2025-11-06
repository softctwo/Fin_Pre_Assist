# 测试文档

## 测试概述

本文档描述了金融售前方案辅助系统的完整测试方案，包括单元测试、集成测试和端到端测试。

## 测试层级

### 1. 单元测试 (Unit Tests)

测试单个组件和服务的功能。

**测试文件**:
- `test_vector_service.py` - 向量服务测试
- `test_document_processor.py` - 文档处理器测试
- `test_template_service.py` - 模板服务测试
- `test_export_service.py` - 导出服务测试

**覆盖范围**:
- ✅ 向量化功能
- ✅ 文档解析
- ✅ 模板渲染
- ✅ 文档导出

### 2. API集成测试 (Integration Tests)

测试API端点的功能和集成。

**测试文件**:
- `test_api_integration.py` - API集成测试

**覆盖的API**:
- ✅ 认证API (注册、登录、获取当前用户)
- ✅ 文档管理API (上传、列表、详情、删除)
- ✅ 方案API (创建、列表、详情、更新、删除)
- ✅ 模板API (创建、列表、预览、变量提取)
- ✅ 知识库API (创建、列表、搜索)
- ✅ 搜索API (语义搜索、统计)

### 3. 端到端测试 (E2E Tests)

测试完整的用户工作流程。

**测试文件**:
- `test_e2e.py` - 端到端功能测试

**测试场景**:
1. 用户注册和登录
2. 文档上传和管理
3. 知识库创建和搜索
4. 模板创建和预览
5. 方案创建和生成
6. 语义搜索功能

## 运行测试

### 快速开始

```bash
cd backend

# 运行所有测试
bash run_tests.sh

# 或使用pytest直接运行
pytest tests/ -v
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/test_vector_service.py -v

# 运行集成测试
pytest tests/test_api_integration.py -v

# 运行端到端测试
python tests/test_e2e.py
```

### 生成测试报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 生成HTML测试报告
pytest tests/ --html=report.html --self-contained-html
```

## 测试覆盖率

### 目标覆盖率

- **单元测试**: > 80%
- **集成测试**: > 70%
- **核心功能**: 100%

### 当前覆盖情况

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| vector_service | ~85% | ✅ |
| document_processor | ~90% | ✅ |
| template_service | ~95% | ✅ |
| export_service | ~80% | ✅ |
| API endpoints | ~75% | ✅ |

## 测试数据

### 测试用户

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpass123"
}
```

### 测试文档

- 文本文件: `test.txt`
- Word文档: `test.docx`
- Excel文件: `test.xlsx`
- PDF文件: `test.pdf`

### 测试知识库

```json
{
  "category": "产品介绍",
  "title": "核心银行系统",
  "content": "核心银行系统是金融机构的核心业务处理系统...",
  "tags": ["银行", "核心系统"]
}
```

### 测试模板

```jinja2
# {{ customer_name }} 项目方案

## 客户需求
{{ requirements }}

## 解决方案
{{ solution_overview }}
```

## 测试检查清单

### 功能测试

- [x] 用户认证和授权
- [x] 文档上传和解析
- [x] 向量化和语义搜索
- [x] 知识库管理
- [x] 模板创建和渲染
- [x] 方案生成
- [x] 文档导出 (Word/Excel)

### 性能测试

- [ ] 文档上传性能 (< 5秒)
- [ ] 向量搜索性能 (< 1秒)
- [ ] 方案生成性能 (< 5分钟)
- [ ] 并发请求处理

### 安全测试

- [x] JWT Token验证
- [x] 密码加密存储
- [x] SQL注入防护
- [x] 文件类型验证
- [ ] XSS攻击防护
- [ ] CSRF防护

### 兼容性测试

- [x] Python 3.9+
- [x] SQLite数据库
- [x] PostgreSQL数据库
- [ ] 不同浏览器测试

## 持续集成

### CI/CD配置

建议在以下场景自动运行测试：
- 每次代码提交
- Pull Request创建时
- 主分支合并前
- 定期调度（每日/每周）

### GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app
```

## 常见问题

### Q: 测试数据库如何配置？

A: 测试自动使用SQLite内存数据库，无需额外配置。测试完成后自动清理。

### Q: 向量数据库测试会影响生产数据吗？

A: 不会。测试使用独立的测试目录 (`test_chroma`)，测试后自动清理。

### Q: 如何模拟AI生成功能？

A: 测试中可以mock AI服务返回固定内容，避免调用实际API。

### Q: 端到端测试需要启动服务吗？

A: 是的。运行 `test_e2e.py` 前需要先启动后端服务:
```bash
python app/main.py
```

## 测试最佳实践

1. **独立性**: 每个测试应该独立运行，不依赖其他测试
2. **可重复性**: 测试结果应该可重复
3. **快速性**: 单元测试应该在秒级完成
4. **清晰性**: 测试名称应该清楚说明测试内容
5. **覆盖性**: 关键路径必须有测试覆盖

## 调试测试

### 查看详细输出

```bash
pytest tests/ -v -s
```

### 只运行失败的测试

```bash
pytest --lf
```

### 停在第一个失败

```bash
pytest -x
```

### 使用pdb调试

```bash
pytest --pdb
```

## 性能基准

| 操作 | 预期时间 | 实际时间 | 状态 |
|------|---------|----------|------|
| 文档上传 | < 5s | - | 待测 |
| 向量化 | < 3s | - | 待测 |
| 语义搜索 | < 1s | - | 待测 |
| 方案生成 | < 5min | - | 待测 |
| Word导出 | < 3s | - | 待测 |
| Excel导出 | < 2s | - | 待测 |

## 下一步

- [ ] 添加性能测试
- [ ] 添加压力测试
- [ ] 完善安全测试
- [ ] 集成到CI/CD
- [ ] 增加测试覆盖率到90%+

---

**版本**: v1.0.0
**最后更新**: 2025-11-06
**维护者**: 开发团队
