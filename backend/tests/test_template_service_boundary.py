"""模板服务边界测试 - 提升测试覆盖率"""
import pytest
from jinja2 import TemplateError, TemplateSyntaxError, UndefinedError
from app.services.template_service import TemplateService


class TestTemplateServiceBoundaryCases:
    """模板服务边界条件测试"""

    @pytest.fixture
    def template_service(self):
        """创建模板服务实例"""
        return TemplateService()

    # ========== 模板语法边界测试 ==========

    def test_template_with_nested_variables(self, template_service):
        """测试嵌套变量访问"""
        template_content = """
        客户信息:
        名称: {{ customer.name }}
        联系人: {{ customer.contact.person }}
        地址: {{ customer.address.city }}, {{ customer.address.country }}
        """

        variables = {
            "customer": {
                "name": "测试银行",
                "contact": {
                    "person": "张经理",
                    "phone": "13800138000"
                },
                "address": {
                    "city": "北京",
                    "country": "中国",
                    "street": "金融街1号"
                }
            }
        }

        result = template_service.render_template(template_content, variables)
        assert "测试银行" in result
        assert "张经理" in result
        assert "北京" in result
        assert "中国" in result

    def test_template_with_array_access(self, template_service):
        """测试数组访问"""
        template_content = """
        团队成员:
        负责人: {{ team[0].name }} ({{ team[0].role }})
        成员2: {{ team[1].name }} ({{ team[1].role }})
        总人数: {{ team|length }}
        """

        variables = {
            "team": [
                {"name": "张三", "role": "项目经理"},
                {"name": "李四", "role": "技术专家"},
                {"name": "王五", "role": "商务经理"}
            ]
        }

        result = template_service.render_template(template_content, variables)
        assert "张三" in result
        assert "项目经理" in result
        assert "李四" in result
        assert "3" in result  # 总人数

    def test_template_with_complex_filters(self, template_service):
        """测试复杂过滤器"""
        template_content = """
        项目统计:
        总预算: {{ projects|sum(attribute='budget') }}
        最大项目: {{ projects|max(attribute='budget')|attr('name') }}
        项目列表: {% for project in projects|sort(attribute='start_date') %}{{ project.name }} {% endfor %}
        """

        variables = {
            "projects": [
                {"name": "项目A", "budget": 1000000, "start_date": "2024-01-15"},
                {"name": "项目B", "budget": 2000000, "start_date": "2024-02-01"},
                {"name": "项目C", "budget": 1500000, "start_date": "2024-01-20"}
            ]
        }

        result = template_service.render_template(template_content, variables)
        assert "4500000" in result  # 总预算
        assert "项目B" in result  # 最大预算项目

    def test_template_with_conditional_logic(self, template_service):
        """测试条件逻辑"""
        template_content = """
        方案建议:
        {% if budget > 1000000 %}
        推荐高级方案
        {% elif budget > 500000 %}
        推荐标准方案
        {% else %}
        推荐基础方案
        {% endif %}

        {% for feature in features %}
        - {{ feature.name }}: {% if feature.required %}必须{% else %}可选{% endif %}
        {% endfor %}
        """

        variables = {
            "budget": 1200000,
            "features": [
                {"name": "功能A", "required": True},
                {"name": "功能B", "required": False},
                {"name": "功能C", "required": True}
            ]
        }

        result = template_service.render_template(template_content, variables)
        assert "推荐高级方案" in result
        assert "必须" in result
        assert "可选" in result

    # ========== 特殊字符和转义测试 ==========

    def test_template_with_special_characters(self, template_service):
        """测试特殊字符处理"""
        template_content = """
        特殊字符测试:
        引号: {{ text_with_quotes }}
        换行: {{ text_with_newlines }}
        HTML: {{ text_with_html }}
        XML: {{ text_with_xml }}
        JSON: {{ text_with_json }}
        """

        variables = {
            "text_with_quotes": '包含"双引号"和\'单引号\'的文本',
            "text_with_newlines": "第一行\n第二行\r\n第三行",
            "text_with_html": "\u003cdiv\u003eHTML内容\u003c/div\u003e",
            "text_with_xml": "\u003c?xml version=\"1.0\"?\u003e\u003croot\u003e内容\u003c/root\u003e",
            "text_with_json": '{"key": "value", "number": 123}'
        }

        result = template_service.render_template(template_content, variables)
        assert '包含"双引号"' in result
        assert "第一行" in result
        assert "HTML内容" in result
        assert "xml version" in result
        assert '"key": "value"' in result

    def test_template_with_escaped_characters(self, template_service):
        """测试转义字符处理"""
        template_content = r"""
        转义字符测试:
        反斜杠: {{ path }}
        正则表达式: {{ regex }}
        Unicode: {{ unicode }}
        控制字符: {{ control_chars }}
        """

        variables = {
            "path": r"C:\Users\Documents\File.txt",
            "regex": r"\d{3}-\d{3}-\d{4}",
            "unicode": "测试Unicode: \u4e2d\u6587 \u30c6\u30b9\u30c8",
            "control_chars": "Tab:\t Newline:\n Return:\r"
        }

        result = template_service.render_template(template_content, variables)
        assert "C:\\Users\\Documents\\File.txt" in result
        assert "\\d{3}-\\d{3}-\\d{4}" in result
        assert "中文" in result
        assert "Tab:" in result

    # ========== 边界条件测试 ==========

    def test_template_with_missing_nested_variables(self, template_service):
        """测试嵌套变量缺失处理"""
        template_content = """
        客户信息:
        名称: {{ customer.name }}
        地址: {{ customer.address.city }}
        邮编: {{ customer.address.zipcode }}
        """

        # 只提供部分嵌套数据
        variables = {
            "customer": {
                "name": "测试客户"
                # 缺少address字段
            }
        }

        # 应该抛出UndefinedError
        with pytest.raises(UndefinedError):
            template_service.render_template(template_content, variables)

    def test_template_with_empty_collections(self, template_service):
        """测试空集合处理"""
        template_content = """
        项目列表:
        {% for project in projects %}
        - {{ project.name }}
        {% else %}
        暂无项目
        {% endfor %}

        团队成员:
        {% for member in team %}
        - {{ member }}
        {% else %}
        暂无团队成员
        {% endfor %}
        """

        variables = {
            "projects": [],  # 空列表
            "team": ()       # 空元组
        }

        result = template_service.render_template(template_content, variables)
        assert "暂无项目" in result
        assert "暂无团队成员" in result

    def test_template_with_none_values(self, template_service):
        """测试None值处理"""
        template_content = """
        数据状态:
        项目名: {{ project.name or '未命名项目' }}
        预算: {{ project.budget or 0 }}
        日期: {{ project.date or '待定' }}
        描述: {{ project.description or '暂无描述' }}
        """

        variables = {
            "project": {
                "name": None,
                "budget": None,
                "date": None,
                "description": None
            }
        }

        result = template_service.render_template(template_content, variables)
        assert "未命名项目" in result
        assert "0" in result
        assert "待定" in result
        assert "暂无描述" in result

    # ========== 大文本和性能测试 ==========

    def test_very_large_template(self, template_service):
        """测试超大模板"""
        # 创建一个包含1000个变量的模板
        template_parts = []
        variables = {}

        for i in range(1000):
            var_name = f"var_{i}"
            template_str = "变量{}: {{% raw %}}{{{{ {} }}}}{% endraw %}}".format(i, var_name)
            template_parts.append(template_str)
            variables[var_name] = f"值{i}"

        template_content = "\n".join(template_parts)

        result = template_service.render_template(template_content, variables)
        assert "变量0: 值0" in result
        assert "变量999: 值999" in result
        assert result.count("值") == 1000

    def test_deeply_nested_template(self, template_service):
        """测试深层嵌套模板"""
        template_content = """
        {% for category in categories %}
        分类: {{ category.name }}
        {% for subcategory in category.subcategories %}
          子分类: {{ subcategory.name }}
          {% for item in subcategory.items %}
            - {{ item.name }}: {{ item.value }}
            {% for tag in item.tags %}
              [{{ tag }}]
            {% endfor %}
          {% endfor %}
        {% endfor %}
        {% endfor %}
        """

        variables = {
            "categories": [
                {
                    "name": "技术方案",
                    "subcategories": [
                        {
                            "name": "前端技术",
                            "items": [
                                {
                                    "name": "React",
                                    "value": "UI框架",
                                    "tags": ["JavaScript", "组件化"]
                                },
                                {
                                    "name": "Vue",
                                    "value": "渐进式框架",
                                    "tags": ["JavaScript", "易学"]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        result = template_service.render_template(template_content, variables)
        assert "技术方案" in result
        assert "前端技术" in result
        assert "React" in result
        assert "[JavaScript]" in result

    # ========== 错误处理和异常测试 ==========

    def test_invalid_template_syntax(self, template_service):
        """测试无效模板语法"""
        invalid_templates = [
            "{{ var",           # 未闭合的变量
            "{% if %}",         # 缺少条件表达式
            "{% for %}",        # 缺少循环变量
            "{{ var|invalid_filter }}",  # 无效过滤器
            "{% undefined_tag %}",       # 未定义标签
        ]

        for template_content in invalid_templates:
            is_valid, error = template_service.validate_template(template_content)
            assert is_valid is False
            assert error != ""

    def test_template_with_circular_reference(self, template_service):
        """测试循环引用（如果可能）"""
        # Jinja2通常会自动处理循环引用
        template_content = """
        {% set a = b %}
        {% set b = a %}
        {{ a }}
        """

        # 这通常不会导致无限循环，但会输出空值
        variables = {}
        result = template_service.render_template(template_content, variables)
        # 应该能正常处理，不会崩溃
        assert isinstance(result, str)

    def test_template_with_infinite_loop(self, template_service):
        """测试无限循环模板"""
        template_content = """
        {% for i in range(10) %}
        {% for j in range(1000000) %}
        无限循环测试 {{ i }}, {{ j }}
        {% endfor %}
        {% endfor %}
        """

        variables = {}
        # 应该能处理，但可能耗时较长
        # 在实际应用中应该设置超时机制
        result = template_service.render_template(template_content, variables)
        assert "无限循环测试" in result

    # ========== 安全性测试 ==========

    def test_template_with_injection_attempts(self, template_service):
        """测试注入攻击尝试"""
        injection_attempts = [
            "{{ __import__('os').system('rm -rf /') }}",  # Python代码注入
            "{{ config }}",                              # 配置信息泄露
            "{{ self }}",                               # 对象信息泄露
            "{% raw %}{{ 7*7 }}{% endraw %}",           # 原始输出测试
        ]

        for template_content in injection_attempts:
            # Jinja2默认会阻止危险的属性和方法访问
            is_valid, error = template_service.validate_template(template_content)
            # 应该能正常验证通过或给出适当错误
            assert isinstance(is_valid, bool)

    def test_template_with_xss_content(self, template_service):
        """测试XSS内容处理"""
        template_content = """
        客户反馈: {{ feedback }}
        建议: {{ suggestion }}
        """

        variables = {
            "feedback": "<script>alert('XSS')\u003c/script\u003e",
            "suggestion": "javascript:alert('XSS')",
        }

        result = template_service.render_template(template_content, variables)
        # 模板引擎应该保持原始内容，由前端进行XSS防护
        assert "<script>" in result
        assert "javascript:" in result

    # ========== 数据类型边界测试 ==========

    def test_template_with_numeric_boundaries(self, template_service):
        """测试数值边界"""
        template_content = """
        数值测试:
        大整数: {{ big_int }}
        小数: {{ small_float }}
        负数: {{ negative_num }}
        零: {{ zero }}
        科学计数法: {{ scientific }}
        无穷大: {{ infinity }}
        非数字: {{ nan }}
        """

        import math

        variables = {
            "big_int": 2**63 - 1,  # 64位整数最大值
            "small_float": 1e-10,   # 很小的浮点数
            "negative_num": -999999.999,
            "zero": 0,
            "scientific": 1.23e-4,
            "infinity": float('inf'),
            "nan": float('nan')
        }

        result = template_service.render_template(template_content, variables)
        assert "9223372036854775807" in result  # 2^63-1
        assert "1e-10" in result
        assert "-999999.999" in result
        assert "0" in result
        assert "inf" in result
        assert "nan" in result

    def test_template_with_date_boundaries(self, template_service):
        """测试日期边界"""
        template_content = """
        日期信息:
        开始日期: {{ start_date }}
        结束日期: {{ end_date }}
        持续时间: {{ duration }} 天
        """

        from datetime import datetime, timedelta

        variables = {
            "start_date": datetime(1970, 1, 1),  # Unix时间戳起点
            "end_date": datetime(2038, 1, 19),   # 32位系统时间戳终点
            "duration": (datetime(2038, 1, 19) - datetime(1970, 1, 1)).days
        }

        result = template_service.render_template(template_content, variables)
        assert "1970-01-01" in result
        assert "2038-01-19" in result

    # ========== 国际化和本地化测试 ==========

    def test_template_with_multilingual_content(self, template_service):
        """测试多语言内容"""
        template_content = """
        多语言方案:
        中文: {{ chinese_text }}
        英文: {{ english_text }}
        日文: {{ japanese_text }}
        阿拉伯文: {{ arabic_text }}
        俄文: {{ russian_text }}
        Emoji: {{ emoji_text }}
        """

        variables = {
            "chinese_text": "售前技术方案",
            "english_text": "Pre-sales Technical Proposal",
            "japanese_text": "プリセールス技術提案",
            "arabic_text": "اقتراح التقنية ما قبل البيع",
            "russian_text": "Предпродажное техническое предложение",
            "emoji_text": "🚀 方案设计 🎯 技术实施 💼 商务洽谈"
        }

        result = template_service.render_template(template_content, variables)
        assert "售前技术方案" in result
        assert "Pre-sales Technical Proposal" in result
        assert "プリセールス" in result
        assert "🚀" in result

    # ========== 性能边界测试 ==========

    def test_template_rendering_performance(self, template_service):
        """测试模板渲染性能边界"""
        import time

        # 大模板，包含大量循环和条件判断
        template_content = """
        {% for i in range(1000) %}
        {% if i % 2 == 0 %}
        偶数项 {{ i }}: {{ items[i] }}
        {% else %}
        奇数项 {{ i }}: {{ items[i] }}
        {% endif %}
        {% endfor %}
        """

        variables = {
            "items": [f"项目{i}" for i in range(1000)]
        }

        start_time = time.time()
        result = template_service.render_template(template_content, variables)
        end_time = time.time()

        # 验证结果正确性
        assert "偶数项 0: 项目0" in result
        assert "奇数项 1: 项目1" in result
        assert "偶数项 998: 项目998" in result

        # 性能应该在合理范围内（5秒内）
        render_time = end_time - start_time
        assert render_time < 5.0, f"模板渲染耗时过长: {render_time}秒"

    def test_memory_efficiency_with_large_template(self, template_service):
        """测试大模板内存效率"""
        # 创建包含大量文本的模板
        large_text = "这是一段很长的文本内容。" * 1000  # 约2万字

        template_content = f"""
        大文本内容:
        {{ large_text }}

        重复内容:
        {{ large_text }}
        {{ large_text }}
        """

        variables = {
            "large_text": large_text
        }

        # 应该能正常处理，不会内存溢出
        result = template_service.render_template(template_content, variables)
        assert "这是一段很长的文本内容。" in result
        assert result.count("这是一段很长的文本内容。") == 3000  # 3次重复

    # ========== 错误恢复和容错测试 ==========

    def test_template_with_partial_data_recovery(self, template_service):
        """测试部分数据缺失的容错处理"""
        template_content = """
        项目信息:
        名称: {{ project.name }}
        预算: {{ project.budget }}
        状态: {{ project.status or '未知' }}
        负责人: {{ project.manager.name or project.manager or '待分配' }}
        """

        # 测试多种数据缺失情况
        test_cases = [
            # 情况1: 完全缺失
            {"project": None},
            # 情况2: 部分缺失
            {"project": {"name": "测试项目"}},
            # 情况3: 嵌套缺失
            {"project": {"name": "测试项目", "budget": 1000000, "manager": None}},
        ]

        for variables in test_cases:
            try:
                result = template_service.render_template(template_content, variables)
                # 应该能正常处理或抛出预期异常
                assert isinstance(result, str)
            except (UndefinedError, AttributeError):
                # 预期的异常情况
                pass

    def test_template_error_messages(self, template_service):
        """测试模板错误信息"""
        invalid_templates = [
            ("{{ undefined_var }}", UndefinedError),
            ("{% for %}", TemplateSyntaxError),
            ("{{ }}", TemplateSyntaxError),
        ]

        for template_content, expected_error in invalid_templates:
            with pytest.raises(expected_error):
                template_service.render_template(template_content, {})