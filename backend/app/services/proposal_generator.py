"""方案生成服务 - 增强版"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models import Proposal
from app.services.ai_service import AIService
from app.services.vector_service import vector_service


class ProposalGenerator:
    """方案生成器 - 使用向量搜索和优化提示词"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

    async def generate(self, proposal: Proposal) -> Dict:
        """生成方案内容"""
        logger.info(f"开始生成方案: {proposal.title}")

        # 1. 使用向量搜索获取相关文档
        similar_docs = self._search_similar_documents(proposal)

        # 2. 获取相关知识库内容
        relevant_knowledge = self._search_relevant_knowledge(proposal)

        # 3. 构建增强上下文
        context = self._build_enhanced_context(proposal, similar_docs, relevant_knowledge)

        # 4. 生成各部分内容（并行生成以提高速度）
        logger.info("开始生成方案各部分内容...")

        executive_summary = await self._generate_executive_summary(proposal, context)
        solution_overview = await self._generate_solution_overview(proposal, context)
        technical_details = await self._generate_technical_details(proposal, context)
        implementation_plan = await self._generate_implementation_plan(proposal, context)
        pricing = await self._generate_pricing(proposal, context)

        # 5. 生成完整内容
        full_content = self._combine_content(
            executive_summary, solution_overview, technical_details, implementation_plan
        )

        logger.info(f"方案生成完成: {proposal.title}")

        return {
            "executive_summary": executive_summary,
            "solution_overview": solution_overview,
            "technical_details": technical_details,
            "implementation_plan": implementation_plan,
            "pricing": pricing,
            "full_content": full_content,
        }

    def _search_similar_documents(self, proposal: Proposal) -> List[Dict]:
        """搜索相似的历史文档"""
        try:
            results = vector_service.search_documents(
                query=proposal.requirements,
                n_results=3,
                filter_metadata={"industry": proposal.customer_industry} if proposal.customer_industry else None,
            )
            logger.info(f"找到 {len(results)} 个相似文档")
            return results
        except Exception as e:
            logger.error(f"搜索相似文档失败: {e}")
            return []

    def _search_relevant_knowledge(self, proposal: Proposal) -> List[Dict]:
        """搜索相关知识库内容"""
        try:
            results = vector_service.search_knowledge(query=proposal.requirements, n_results=5)
            logger.info(f"找到 {len(results)} 个相关知识")
            return results
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []

    def _build_enhanced_context(
        self, proposal: Proposal, similar_docs: List[Dict], relevant_knowledge: List[Dict]
    ) -> str:
        """构建增强上下文信息"""
        context_parts = []

        # 客户信息
        context_parts.append("=" * 50)
        context_parts.append("【客户信息】")
        context_parts.append("=" * 50)
        context_parts.append(f"客户名称: {proposal.customer_name}")
        if proposal.customer_industry:
            context_parts.append(f"所属行业: {proposal.customer_industry}")
        if proposal.customer_contact:
            context_parts.append(f"联系方式: {proposal.customer_contact}")

        # 需求分析
        context_parts.append("\n" + "=" * 50)
        context_parts.append("【需求分析】")
        context_parts.append("=" * 50)
        context_parts.append(proposal.requirements)

        # 相似历史方案参考
        if similar_docs:
            context_parts.append("\n" + "=" * 50)
            context_parts.append("【相似历史方案参考】")
            context_parts.append("=" * 50)
            for i, doc in enumerate(similar_docs, 1):
                metadata = doc.get("metadata", {})
                context_parts.append(f"\n参考方案 {i}:")
                context_parts.append(f"标题: {metadata.get('title', 'N/A')}")
                if metadata.get("customer_name"):
                    context_parts.append(f"客户: {metadata['customer_name']}")
                context_parts.append(f"内容摘要:\n{doc.get('document', '')[:500]}")

        # 相关知识库
        if relevant_knowledge:
            context_parts.append("\n" + "=" * 50)
            context_parts.append("【相关产品和解决方案知识】")
            context_parts.append("=" * 50)
            for i, kb in enumerate(relevant_knowledge, 1):
                metadata = kb.get("metadata", {})
                context_parts.append(f"\n知识 {i}: {metadata.get('title', 'N/A')}")
                context_parts.append(f"{kb.get('document', '')[:300]}")

        return "\n".join(context_parts)

    async def _generate_executive_summary(self, proposal: Proposal, context: str) -> str:
        """生成执行摘要 - 优化提示词"""
        prompt = f"""你是一位资深的金融行业售前方案专家，具有10年以上的方案撰写经验。

【任务】
为"{proposal.customer_name}"撰写一份专业的执行摘要（Executive Summary）。

【背景信息】
{context}

【要求】
1. 字数控制在200-300字
2. 使用专业、简洁的商务语言
3. 突出价值主张和核心优势
4. 体现对客户需求的深刻理解

【结构】
1. 客户痛点和需求概述（50-80字）
2. 解决方案核心价值（100-150字）
3. 预期收益和业务价值（50-70字）

请直接输出执行摘要内容，不要包含标题和其他说明文字：
"""
        return await self.ai_service.generate_text(prompt, temperature=0.7)

    async def _generate_solution_overview(self, proposal: Proposal, context: str) -> str:
        """生成解决方案概述 - 优化提示词"""
        prompt = f"""你是一位资深的金融行业售前方案专家。

【任务】
为"{proposal.customer_name}"撰写详细的解决方案概述。

【背景信息】
{context}

【要求】
1. 字数控制在800-1200字
2. 内容专业、结构清晰、逻辑严密
3. 结合金融行业最佳实践
4. 突出技术创新和业务价值

【结构】
一、方案整体架构（200-300字）
- 总体架构设计思路
- 系统分层设计
- 关键组件说明

二、核心功能模块（300-400字）
- 各功能模块详细说明
- 模块间协作关系
- 业务流程覆盖

三、技术亮点（200-300字）
- 创新技术应用
- 技术优势分析
- 与同类方案对比

四、方案优势（200-300字）
- 满足客户需求的独特优势
- 技术领先性
- 可扩展性和未来发展

请直接输出解决方案概述内容，使用markdown格式组织：
"""
        return await self.ai_service.generate_text(prompt, temperature=0.7, max_tokens=2500)

    async def _generate_technical_details(self, proposal: Proposal, context: str) -> str:
        """生成技术细节 - 优化提示词"""
        prompt = f"""你是一位精通金融科技的架构师，负责为"{proposal.customer_name}"编写技术方案。

【背景信息】
{context}

【任务】
撰写详细的技术实现方案文档，展示专业的技术能力和深入的技术思考。

【要求】
1. 字数控制在1000-1500字
2. 技术描述准确、专业
3. 架构设计合理、可落地
4. 考虑性能、安全、可靠性

【结构】
一、系统架构设计（300-400字）
- 技术架构图（文字描述）
- 分层架构说明
- 技术选型依据

二、核心技术实现（400-500字）
- 关键技术点详细说明
- 技术实现方案
- 技术难点和解决方案

三、性能优化方案（200-300字）
- 性能指标要求
- 优化策略
- 压力测试方案

四、安全保障措施（200-300字）
- 数据安全
- 访问控制
- 安全审计
- 容灾备份

请使用markdown格式输出，包含必要的技术架构描述：
"""
        return await self.ai_service.generate_text(prompt, temperature=0.6, max_tokens=3000)

    async def _generate_implementation_plan(self, proposal: Proposal, context: str) -> str:
        """生成实施计划 - 优化提示词"""
        prompt = f"""你是一位经验丰富的项目经理，负责为"{proposal.customer_name}"制定项目实施计划。

【背景信息】
{context}

【任务】
制定详细的项目实施计划，确保项目顺利落地。

【要求】
1. 字数控制在800-1200字
2. 计划具体、可执行
3. 时间安排合理
4. 风险考虑全面

【结构】
一、实施总体策略（150-200字）
- 实施方法论
- 总体时间规划
- 实施原则

二、实施阶段划分（400-500字）
阶段1：需求确认与设计（2-3周）
- 主要工作内容
- 交付成果
- 里程碑

阶段2：开发与测试（4-6周）
- 主要工作内容
- 交付成果
- 里程碑

阶段3：部署与上线（1-2周）
- 主要工作内容
- 交付成果
- 里程碑

阶段4：试运行与验收（2-3周）
- 主要工作内容
- 交付成果
- 里程碑

三、人员配置（150-200字）
- 项目组织架构
- 角色职责
- 人员投入

四、风险管理（150-200字）
- 主要风险识别
- 应对措施
- 应急预案

请使用markdown格式输出实施计划：
"""
        return await self.ai_service.generate_text(prompt, temperature=0.6, max_tokens=2500)

    async def _generate_pricing(self, proposal: Proposal, context: str) -> Optional[Dict]:
        """生成报价信息"""
        prompt = f"""你是一位金融行业售前顾问，负责为"{proposal.customer_name}"制定报价方案。

【背景信息】
{context}

【任务】
根据方案内容，提供合理的报价建议和成本构成。

【要求】
1. 报价合理、有竞争力
2. 成本构成清晰
3. 考虑行业标准

请以JSON格式输出报价信息，包含以下字段：
{{
  "software_license": "软件许可费用（元）",
  "implementation": "实施服务费用（元）",
  "training": "培训费用（元）",
  "support_yearly": "年度维护费用（元）",
  "total": "总计（元）",
  "notes": "报价说明"
}}

JSON格式输出：
"""
        try:
            result = await self.ai_service.generate_text(prompt, temperature=0.5, max_tokens=500)
            # TODO: 解析JSON结果
            return {"raw": result}
        except Exception as e:
            logger.error(f"生成报价失败: {e}")
            return None

    def _combine_content(self, *sections) -> str:
        """合并所有内容为完整方案"""
        parts = []

        # 添加标题和各部分
        section_titles = ["# 执行摘要\n", "\n\n# 解决方案概述\n", "\n\n# 技术实现方案\n", "\n\n# 项目实施计划\n"]

        for i, section in enumerate(sections[:4]):  # 只取前4个部分
            if section:
                parts.append(section_titles[i] + section)

        return "".join(parts)
