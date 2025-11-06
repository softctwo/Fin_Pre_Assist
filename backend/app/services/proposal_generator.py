"""方案生成服务"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models import Proposal, Document
from app.services.ai_service import AIService


class ProposalGenerator:
    """方案生成器"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    async def generate(self, proposal: Proposal) -> Dict:
        """生成方案内容"""
        # 1. 获取参考文档
        reference_docs = []
        if proposal.reference_documents:
            reference_docs = self.db.query(Document).filter(
                Document.id.in_(proposal.reference_documents)
            ).all()

        # 2. 构建上下文
        context = self._build_context(proposal, reference_docs)

        # 3. 生成各部分内容
        executive_summary = await self._generate_executive_summary(proposal, context)
        solution_overview = await self._generate_solution_overview(proposal, context)
        technical_details = await self._generate_technical_details(proposal, context)
        implementation_plan = await self._generate_implementation_plan(proposal, context)

        # 4. 生成完整内容
        full_content = self._combine_content(
            executive_summary,
            solution_overview,
            technical_details,
            implementation_plan
        )

        return {
            "executive_summary": executive_summary,
            "solution_overview": solution_overview,
            "technical_details": technical_details,
            "implementation_plan": implementation_plan,
            "full_content": full_content,
            "pricing": None  # TODO: 实现报价生成
        }

    def _build_context(self, proposal: Proposal, reference_docs: List[Document]) -> str:
        """构建上下文信息"""
        context_parts = []

        # 添加客户信息
        context_parts.append(f"客户名称: {proposal.customer_name}")
        if proposal.customer_industry:
            context_parts.append(f"所属行业: {proposal.customer_industry}")

        # 添加需求
        context_parts.append(f"\n客户需求:\n{proposal.requirements}")

        # 添加参考文档内容
        if reference_docs:
            context_parts.append("\n参考历史方案:")
            for doc in reference_docs:
                if doc.content_text:
                    context_parts.append(f"\n--- {doc.title} ---")
                    context_parts.append(doc.content_text[:2000])  # 限制长度

        return "\n".join(context_parts)

    async def _generate_executive_summary(self, proposal: Proposal, context: str) -> str:
        """生成执行摘要"""
        prompt = f"""
基于以下信息，生成一份专业的执行摘要：

{context}

请生成一份简洁的执行摘要（200-300字），包括：
1. 客户需求概述
2. 解决方案核心价值
3. 预期收益

执行摘要：
"""
        return await self.ai_service.generate_text(prompt)

    async def _generate_solution_overview(self, proposal: Proposal, context: str) -> str:
        """生成解决方案概述"""
        prompt = f"""
基于以下信息，生成解决方案概述：

{context}

请生成详细的解决方案概述（500-800字），包括：
1. 方案整体架构
2. 核心功能模块
3. 技术亮点
4. 方案优势

解决方案概述：
"""
        return await self.ai_service.generate_text(prompt)

    async def _generate_technical_details(self, proposal: Proposal, context: str) -> str:
        """生成技术细节"""
        prompt = f"""
基于以下信息，生成技术细节说明：

{context}

请生成详细的技术说明（800-1200字），包括：
1. 系统架构设计
2. 技术栈选择
3. 关键技术实现
4. 性能和安全考虑

技术细节：
"""
        return await self.ai_service.generate_text(prompt)

    async def _generate_implementation_plan(self, proposal: Proposal, context: str) -> str:
        """生成实施计划"""
        prompt = f"""
基于以下信息，生成项目实施计划：

{context}

请生成详细的实施计划（600-1000字），包括：
1. 实施阶段划分
2. 各阶段主要工作
3. 时间安排
4. 人员配置
5. 风险控制

实施计划：
"""
        return await self.ai_service.generate_text(prompt)

    def _combine_content(self, *sections) -> str:
        """合并所有内容"""
        return "\n\n".join(filter(None, sections))
