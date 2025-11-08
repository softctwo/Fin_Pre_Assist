"""安全工具模块 - XSS防护、输入验证等"""

import html
import re
from typing import Any, Dict
from loguru import logger


class XSSProtector:
    """XSS防护工具类"""

    # 危险标签和属性模式
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # script标签
        r"javascript:",  # javascript:协议
        r"on\w+\s*=",  # 事件处理器
        r"<iframe[^>]*>.*?</iframe>",  # iframe标签
        r"<object[^>]*>.*?</object>",  # object标签
        r"<embed[^>]*>.*?</embed>",  # embed标签
        r"<form[^>]*>.*?</form>",  # form标签
    ]

    @staticmethod
    def sanitize_html(content: str) -> str:
        """
        清理HTML内容，防止XSS攻击

        Args:
            content: 原始内容

        Returns:
            清理后的内容
        """
        if not content:
            return content

        # 先进行HTML转义
        sanitized = html.escape(content)

        # 解码常用HTML实体，保留基本格式
        html_entities = {
            "&amp;lt;": "&lt;",
            "&amp;gt;": "&gt;",
            "&amp;amp;": "&amp;",
            "&amp;quot;": "&quot;",
            "&amp;#39;": "&#39;",
        }

        for entity, replacement in html_entities.items():
            sanitized = sanitized.replace(entity, replacement)

        return sanitized

    @staticmethod
    def sanitize_input(content: str) -> str:
        """
        清理用户输入，移除危险内容

        Args:
            content: 用户输入

        Returns:
            安全的输入内容
        """
        if not content:
            return content

        # 移除危险的JavaScript协议
        content = re.sub(r"javascript:", "", content, flags=re.IGNORECASE)

        # 移除危险的事件处理器
        content = re.sub(r"on\w+\s*=", "on_cancelled=", content, flags=re.IGNORECASE)

        # 对剩余的HTML标签进行转义
        content = html.escape(content)

        return content

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理字典中的所有字符串值

        Args:
            data: 原始字典

        Returns:
            清理后的字典
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # 对内容进行清理，但不过度转义
                sanitized[key] = XSSProtector.sanitize_input(value)
            elif isinstance(value, dict):
                sanitized[key] = XSSProtector.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    XSSProtector.sanitize_input(item) if isinstance(item, str) else item for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    @staticmethod
    def is_dangerous_content(content: str) -> bool:
        """
        检测内容是否包含危险模式

        Args:
            content: 待检测内容

        Returns:
            是否包含危险内容
        """
        if not content:
            return False

        for pattern in XSSProtector.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                logger.warning(f"检测到危险内容模式: {pattern}")
                return True

        return False

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL是否安全

        Args:
            url: 待验证的URL

        Returns:
            URL是否安全
        """
        if not url:
            return True

        # 检查危险的URL协议
        dangerous_protocols = ["javascript:", "vbscript:", "data:", "file:"]
        url_lower = url.lower().strip()

        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                logger.warning(f"检测到危险URL协议: {protocol}")
                return False

        return True


def sanitize_for_api(data: Any) -> Any:
    """
    API数据清理的快捷函数

    Args:
        data: 待清理的数据

    Returns:
        清理后的数据
    """
    if isinstance(data, str):
        return XSSProtector.sanitize_input(data)
    elif isinstance(data, dict):
        return XSSProtector.sanitize_dict(data)
    elif isinstance(data, list):
        return [sanitize_for_api(item) for item in data]
    else:
        return data
