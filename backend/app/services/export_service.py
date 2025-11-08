""" 文档导出服务"""

import os
from datetime import datetime
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from loguru import logger

from app.core.config import settings
from app.models import Proposal


class ExportService:
    """文档导出服务"""

    @staticmethod
    def export_proposal_to_word(proposal: Proposal) -> str:
        """导出方案为Word文档"""
        try:
            # 创建Word文档
            doc = docx.Document()

            # 设置文档样式
            ExportService._set_word_styles(doc)

            # 添加标题
            title = doc.add_heading(proposal.title, 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # 添加文档信息
            doc.add_paragraph(f"客户名称: {proposal.customer_name}")
            doc.add_paragraph(f"创建时间: {proposal.created_at.strftime('%Y年%m月%d日')}")
            if proposal.customer_industry:
                doc.add_paragraph(f"所属行业: {proposal.customer_industry}")

            doc.add_paragraph()  # 空行
            doc.add_page_break()  # 分页

            # 1. 客户需求
            doc.add_heading("一、客户需求", level=1)
            ExportService._add_paragraph_with_indent(doc, proposal.requirements)
            doc.add_page_break()

            # 2. 执行摘要
            if proposal.executive_summary:
                doc.add_heading("二、执行摘要", level=1)
                ExportService._add_markdown_content(doc, proposal.executive_summary)
                doc.add_page_break()

            # 3. 解决方案概述
            if proposal.solution_overview:
                doc.add_heading("三、解决方案概述", level=1)
                ExportService._add_markdown_content(doc, proposal.solution_overview)
                doc.add_page_break()

            # 4. 技术实现方案
            if proposal.technical_details:
                doc.add_heading("四、技术实现方案", level=1)
                ExportService._add_markdown_content(doc, proposal.technical_details)
                doc.add_page_break()

            # 5. 项目实施计划
            if proposal.implementation_plan:
                doc.add_heading("五、项目实施计划", level=1)
                ExportService._add_markdown_content(doc, proposal.implementation_plan)

            # 保存文档
            filename = f"proposal_{proposal.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
            filepath = os.path.join(settings.EXPORT_DIR, filename)
            doc.save(filepath)

            logger.info(f"Word文档导出成功: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"导出Word文档失败: {e}")
            raise

    @staticmethod
    def export_proposal_to_pdf(proposal: Proposal) -> str:
        """导出方案为PDF文档"""
        try:
            # 先导出为Word
            word_file = ExportService.export_proposal_to_word(proposal)

            # TODO: 使用python-docx2pdf或其他库转换为PDF
            # 这里暂时返回Word文件路径
            # 实际生产环境中，需要安装LibreOffice或使用云服务进行转换

            logger.info("PDF导出功能待完善，当前返回Word文档")
            return word_file

        except Exception as e:
            logger.error(f"导出PDF失败: {e}")
            raise

    @staticmethod
    def export_pricing_to_excel(proposal: Proposal) -> str:
        """导出报价单为Excel"""
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "报价单"

            # 设置列宽
            ws.column_dimensions["A"].width = 5
            ws.column_dimensions["B"].width = 30
            ws.column_dimensions["C"].width = 15
            ws.column_dimensions["D"].width = 15
            ws.column_dimensions["E"].width = 20

            # 定义样式
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            title_font = Font(bold=True, size=16)
            border = Border(
                left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin")
            )

            # 标题
            ws.merge_cells("B2:E2")
            title_cell = ws["B2"]
            title_cell.value = f"{proposal.customer_name} - 项目报价单"
            title_cell.font = title_font
            title_cell.alignment = Alignment(horizontal="center", vertical="center")

            # 基本信息
            ws["B4"] = "项目名称:"
            ws["C4"] = proposal.title
            ws["B5"] = "报价日期:"
            ws["C5"] = datetime.now().strftime("%Y年%m月%d日")
            ws["B6"] = "有效期:"
            ws["C6"] = "30天"

            # 表头
            row = 8
            headers = ["序号", "项目名称", "数量", "单价(元)", "小计(元)"]
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=row, column=col)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border

            # 报价项目
            items = [
                ("1", "软件许可费", "1", "200,000", "200,000"),
                ("2", "实施服务费", "1", "100,000", "100,000"),
                ("3", "培训费用", "1", "30,000", "30,000"),
                ("4", "年度维护费", "1", "50,000", "50,000"),
            ]

            row = 9
            total = 0
            for item in items:
                for col, value in enumerate(item, start=1):
                    cell = ws.cell(row=row, column=col)
                    cell.value = value
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border
                row += 1
                if col >= 4:
                    total += int(value.replace(",", ""))

            # 合计
            row += 1
            ws.merge_cells(f"B{row}:D{row}")
            total_label = ws[f"B{row}"]
            total_label.value = "合计"
            total_label.font = Font(bold=True, size=12)
            total_label.alignment = Alignment(horizontal="right", vertical="center")
            total_label.border = border

            total_cell = ws[f"E{row}"]
            total_cell.value = f"{total:,}"
            total_cell.font = Font(bold=True, size=12, color="FF0000")
            total_cell.alignment = Alignment(horizontal="center", vertical="center")
            total_cell.border = border

            # 备注
            row += 3
            ws[f"B{row}"] = "备注:"
            ws[f"B{row}"].font = Font(bold=True)
            row += 1
            ws[f"B{row}"] = "1. 以上报价含税价"
            row += 1
            ws[f"B{row}"] = "2. 付款方式: 签约后30%，验收后70%"
            row += 1
            ws[f"B{row}"] = "3. 实施周期: 3个月"

            # 保存文件
            filename = f"quotation_{proposal.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            filepath = os.path.join(settings.EXPORT_DIR, filename)
            wb.save(filepath)

            logger.info(f"Excel报价单导出成功: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            raise

    @staticmethod
    def _set_word_styles(doc):
        """设置Word文档样式"""
        # 设置正文样式
        style = doc.styles["Normal"]
        style.font.name = "宋体"
        style.font.size = Pt(12)

    @staticmethod
    def _add_paragraph_with_indent(doc, text: str, indent: float = 0.5):
        """添加带缩进的段落"""
        paragraph = doc.add_paragraph(text)
        paragraph.paragraph_format.first_line_indent = Inches(indent)
        paragraph.paragraph_format.line_spacing = 1.5
        return paragraph

    @staticmethod
    def _add_markdown_content(doc, markdown_text: str):
        """将Markdown内容添加到Word文档"""
        # 简单处理：按行分割并添加
        lines = markdown_text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 处理标题
            if line.startswith("###"):
                doc.add_heading(line.replace("###", "").strip(), level=3)
            elif line.startswith("##"):
                doc.add_heading(line.replace("##", "").strip(), level=2)
            elif line.startswith("#"):
                doc.add_heading(line.replace("#", "").strip(), level=1)
            # 处理列表
            elif line.startswith("- ") or line.startswith("* "):
                doc.add_paragraph(line[2:], style="List Bullet")
            elif line[0:2].replace(".", "").isdigit():
                doc.add_paragraph(line.split(".", 1)[1].strip(), style="List Number")
            # 普通段落
            else:
                ExportService._add_paragraph_with_indent(doc, line, indent=0)


# 全局实例
export_service = ExportService()
