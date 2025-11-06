"""模板服务 - 模板渲染和变量替换"""
from typing import Dict, Any, List
import re
from jinja2 import Template, Environment, BaseLoader
from loguru import logger


class TemplateService:
    """模板服务类"""

    def __init__(self):
        # 创建Jinja2环境
        self.env = Environment(loader=BaseLoader())

    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板，替换变量

        Args:
            template_content: 模板内容
            variables: 变量字典

        Returns:
            渲染后的内容
        """
        try:
            template = self.env.from_string(template_content)
            rendered = template.render(**variables)
            logger.info(f"模板渲染成功，替换了 {len(variables)} 个变量")
            return rendered
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            raise

    def extract_variables(self, template_content: str) -> List[str]:
        """
        从模板中提取所有变量名

        支持的变量格式:
        - {{ variable_name }}
        - {{ object.property }}
        - {{ array[0] }}

        Args:
            template_content: 模板内容

        Returns:
            变量名列表
        """
        # 匹配 {{ variable }} 格式
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\}\}'
        matches = re.findall(pattern, template_content)

        # 去重并排序
        variables = sorted(list(set(matches)))
        logger.info(f"从模板中提取了 {len(variables)} 个变量")

        return variables

    def validate_template(self, template_content: str) -> tuple[bool, str]:
        """
        验证模板语法是否正确

        Args:
            template_content: 模板内容

        Returns:
            (是否有效, 错误信息)
        """
        try:
            self.env.from_string(template_content)
            return True, ""
        except Exception as e:
            return False, str(e)

    def preview_template(
        self,
        template_content: str,
        sample_variables: Dict[str, Any]
    ) -> str:
        """
        预览模板渲染效果

        Args:
            template_content: 模板内容
            sample_variables: 示例变量

        Returns:
            预览内容
        """
        try:
            # 提取所有需要的变量
            required_vars = self.extract_variables(template_content)

            # 使用提供的变量，缺失的用占位符
            merged_vars = {}
            for var in required_vars:
                if var in sample_variables:
                    merged_vars[var] = sample_variables[var]
                else:
                    merged_vars[var] = f"[{var}]"

            # 渲染模板
            return self.render_template(template_content, merged_vars)
        except Exception as e:
            logger.error(f"模板预览失败: {e}")
            raise

    def create_proposal_from_template(
        self,
        template_content: str,
        customer_name: str,
        requirements: str,
        **additional_vars
    ) -> str:
        """
        从模板创建方案

        Args:
            template_content: 模板内容
            customer_name: 客户名称
            requirements: 需求
            **additional_vars: 其他变量

        Returns:
            生成的方案内容
        """
        # 构建变量字典
        variables = {
            'customer_name': customer_name,
            'requirements': requirements,
            'date': self._get_current_date(),
            **additional_vars
        }

        return self.render_template(template_content, variables)

    @staticmethod
    def _get_current_date() -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime('%Y年%m月%d日')

    def get_default_variables(self) -> Dict[str, str]:
        """获取默认的模板变量"""
        return {
            'customer_name': '客户名称',
            'customer_industry': '所属行业',
            'project_name': '项目名称',
            'requirements': '客户需求描述',
            'solution_overview': '解决方案概述',
            'technical_details': '技术实现细节',
            'implementation_plan': '实施计划',
            'price': '报价金额',
            'date': self._get_current_date(),
            'company_name': '公司名称',
            'contact_person': '联系人',
            'contact_phone': '联系电话',
            'contact_email': '联系邮箱',
        }


# 全局实例
template_service = TemplateService()
