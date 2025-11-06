"""模板服务测试"""
import pytest
from app.services.template_service import TemplateService


class TestTemplateService:
    """测试模板服务"""

    @pytest.fixture
    def template_service(self):
        """创建模板服务实例"""
        return TemplateService()

    def test_render_template(self, template_service):
        """测试模板渲染"""
        template_content = "客户名称: {{ customer_name }}, 项目: {{ project_name }}"
        variables = {
            "customer_name": "测试银行",
            "project_name": "核心系统升级"
        }

        result = template_service.render_template(template_content, variables)
        assert "测试银行" in result
        assert "核心系统升级" in result

    def test_extract_variables(self, template_service):
        """测试提取变量"""
        template_content = """
        客户: {{ customer_name }}
        项目: {{ project_name }}
        金额: {{ price }}
        """

        variables = template_service.extract_variables(template_content)
        assert "customer_name" in variables
        assert "project_name" in variables
        assert "price" in variables
        assert len(variables) == 3

    def test_validate_template_valid(self, template_service):
        """测试验证有效模板"""
        template_content = "Hello {{ name }}!"
        is_valid, error = template_service.validate_template(template_content)
        assert is_valid is True
        assert error == ""

    def test_validate_template_invalid(self, template_service):
        """测试验证无效模板"""
        template_content = "Hello {{ name !"  # 缺少闭合括号
        is_valid, error = template_service.validate_template(template_content)
        assert is_valid is False
        assert error != ""

    def test_preview_template(self, template_service):
        """测试模板预览"""
        template_content = """
        客户: {{ customer_name }}
        未提供: {{ missing_var }}
        """
        sample_variables = {"customer_name": "测试客户"}

        result = template_service.preview_template(template_content, sample_variables)
        assert "测试客户" in result
        assert "[missing_var]" in result  # 缺失变量应该有占位符

    def test_create_proposal_from_template(self, template_service):
        """测试从模板创建方案"""
        template_content = """
        # 售前方案

        客户名称: {{ customer_name }}
        需求: {{ requirements }}
        日期: {{ date }}
        """

        result = template_service.create_proposal_from_template(
            template_content=template_content,
            customer_name="测试银行",
            requirements="系统升级改造"
        )

        assert "测试银行" in result
        assert "系统升级改造" in result
        assert "年" in result and "月" in result  # 日期应该存在

    def test_get_default_variables(self, template_service):
        """测试获取默认变量"""
        default_vars = template_service.get_default_variables()
        assert "customer_name" in default_vars
        assert "requirements" in default_vars
        assert "date" in default_vars
        assert isinstance(default_vars, dict)
        assert len(default_vars) > 10
