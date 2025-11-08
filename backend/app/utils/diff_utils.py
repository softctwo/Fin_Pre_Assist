"""
版本差异比较工具

使用difflib库计算文本差异，生成结构化的差异结果。
"""

import difflib
from typing import Dict, Any


class DiffUtils:
    """差异比较工具类"""

    @staticmethod
    def calculate_text_diff(text1: str, text2: str) -> Dict[str, Any]:
        """计算两个文本之间的差异

        Args:
            text1: 原始文本（旧版本）
            text2: 新文本（新版本）

        Returns:
            差异结果字典
        """
        if not text1:
            text1 = ""
        if not text2:
            text2 = ""

        # 按行分割
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)

        # 使用difflib生成差异
        diff = list(difflib.unified_diff(lines1, lines2, lineterm=""))

        # 计算相似度
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()

        # 统计变更
        added_lines = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        removed_lines = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

        return {
            "similarity": round(similarity, 4),
            "diff": diff,
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "total_changes": added_lines + removed_lines,
        }

    @staticmethod
    def calculate_html_diff(text1: str, text2: str) -> str:
        """计算HTML格式的差异（用于前端展示）

        Args:
            text1: 原始文本（旧版本）
            text2: 新文本（新版本）

        Returns:
            HTML格式的差异
        """
        if not text1:
            text1 = ""
        if not text2:
            text2 = ""

        differ = difflib.HtmlDiff()
        html_diff = differ.make_table(
            text1.splitlines(), text2.splitlines(), fromdesc="旧版本", todesc="新版本", context=True, numlines=3
        )

        return html_diff

    @staticmethod
    def compare_json_content(content1: Dict[str, Any], content2: Dict[str, Any]) -> Dict[str, Any]:
        """比较两个JSON内容的差异

        Args:
            content1: 旧版本内容
            content2: 新版本内容

        Returns:
            结构化的差异结果
        """
        diff_result = {"fields_changed": {}, "fields_added": [], "fields_removed": [], "summary": {}}

        # 获取所有字段
        all_keys = set(content1.keys()) | set(content2.keys())

        for key in all_keys:
            if key not in content1:
                # 字段新增
                diff_result["fields_added"].append(key)
            elif key not in content2:
                # 字段删除
                diff_result["fields_removed"].append(key)
            elif content1[key] != content2[key]:
                # 字段变更
                if isinstance(content1[key], str) and isinstance(content2[key], str):
                    # 文本字段：计算详细差异
                    text_diff = DiffUtils.calculate_text_diff(content1[key], content2[key])
                    diff_result["fields_changed"][key] = {
                        "old_value": content1[key][:200] + "..." if len(content1[key]) > 200 else content1[key],
                        "new_value": content2[key][:200] + "..." if len(content2[key]) > 200 else content2[key],
                        "similarity": text_diff["similarity"],
                        "changes": text_diff["total_changes"],
                    }
                else:
                    # 非文本字段：直接记录新旧值
                    diff_result["fields_changed"][key] = {"old_value": content1[key], "new_value": content2[key]}

        # 生成摘要
        diff_result["summary"] = {
            "total_fields": len(all_keys),
            "changed_fields": len(diff_result["fields_changed"]),
            "added_fields": len(diff_result["fields_added"]),
            "removed_fields": len(diff_result["fields_removed"]),
        }

        return diff_result

    @staticmethod
    def generate_change_summary(diff_result: Dict[str, Any]) -> str:
        """生成变更摘要文本

        Args:
            diff_result: 差异结果

        Returns:
            变更摘要文本
        """
        summary_parts = []

        summary = diff_result.get("summary", {})

        if summary.get("changed_fields", 0) > 0:
            summary_parts.append(f"修改了 {summary['changed_fields']} 个字段")

        if summary.get("added_fields", 0) > 0:
            summary_parts.append(f"新增了 {summary['added_fields']} 个字段")

        if summary.get("removed_fields", 0) > 0:
            summary_parts.append(f"删除了 {summary['removed_fields']} 个字段")

        if not summary_parts:
            return "无变更"

        return "、".join(summary_parts)

    @staticmethod
    def is_major_change(diff_result: Dict[str, Any], threshold: float = 0.3) -> bool:
        """判断是否为重大变更

        Args:
            diff_result: 差异结果
            threshold: 阈值（默认30%变更视为重大变更）

        Returns:
            是否为重大变更
        """
        summary = diff_result.get("summary", {})
        total_fields = summary.get("total_fields", 0)

        if total_fields == 0:
            return False

        changed_count = (
            summary.get("changed_fields", 0) + summary.get("added_fields", 0) + summary.get("removed_fields", 0)
        )

        change_ratio = changed_count / total_fields

        return change_ratio >= threshold

    @staticmethod
    def compare_proposals(proposal1_content: Dict[str, Any], proposal2_content: Dict[str, Any]) -> Dict[str, Any]:
        """比较两个方案版本的完整差异

        Args:
            proposal1_content: 旧版本方案内容
            proposal2_content: 新版本方案内容

        Returns:
            完整的差异分析结果
        """
        # 关键字段列表
        key_fields = [
            "requirements",
            "executive_summary",
            "solution_overview",
            "technical_details",
            "implementation_plan",
            "full_content",
        ]

        result = {"overview": {}, "field_diffs": {}, "is_major_change": False}

        # 比较每个关键字段
        for field in key_fields:
            if field in proposal1_content or field in proposal2_content:
                text1 = proposal1_content.get(field, "")
                text2 = proposal2_content.get(field, "")

                if isinstance(text1, str) and isinstance(text2, str):
                    diff = DiffUtils.calculate_text_diff(text1, text2)
                    result["field_diffs"][field] = {
                        "similarity": diff["similarity"],
                        "added_lines": diff["added_lines"],
                        "removed_lines": diff["removed_lines"],
                        "total_changes": diff["total_changes"],
                    }

        # 计算整体差异
        json_diff = DiffUtils.compare_json_content(proposal1_content, proposal2_content)
        result["overview"] = json_diff["summary"]
        result["is_major_change"] = DiffUtils.is_major_change(json_diff)
        result["change_summary"] = DiffUtils.generate_change_summary(json_diff)

        return result


# 便捷函数
def compare_versions(version1_content: Dict[str, Any], version2_content: Dict[str, Any]) -> Dict[str, Any]:
    """便捷的版本比较函数

    使用方法：
        diff = compare_versions(old_version.content, new_version.content)
    """
    return DiffUtils.compare_proposals(version1_content, version2_content)
