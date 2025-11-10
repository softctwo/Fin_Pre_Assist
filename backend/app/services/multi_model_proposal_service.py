"""
多模型方案生成服务

支持多个AI模型同时生成方案版本，并支持迭代优化
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Proposal, ProposalVersion, ProposalVersionStatus, User
from app.services.ai_service import ai_service
from app.services.proposal_generator import proposal_generator
import logging

logger = logging.getLogger(__name__)


class MultiModelProposalService:
    """多模型方案生成服务"""

    def __init__(self):
        self.available_models = [
            {"provider": "kimi", "name": "Kimi", "model": "moonshot-v1-8k"},
            {"provider": "zhipu", "name": "智谱AI", "model": "glm-4.6"},
            {"provider": "deepseek", "name": "DeepSeek", "model": "deepseek-chat"},
            # 可以添加更多模型
        ]

    async def generate_proposal_versions(
        self,
        db: Session,
        proposal_id: int,
        selected_models: List[str],
        requirements: str,
        user_id: int,
        iteration_feedback: Optional[str] = None,
        parent_version_id: Optional[int] = None
    ) -> List[ProposalVersion]:
        """
        使用多个AI模型生成方案版本

        Args:
            db: 数据库会话
            proposal_id: 方案ID
            selected_models: 选择的模型提供商列表
            requirements: 需求描述
            user_id: 用户ID
            iteration_feedback: 迭代反馈
            parent_version_id: 父版本ID

        Returns:
            生成的方案版本列表
        """
        # 获取方案信息
        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise ValueError(f"方案 {proposal_id} 不存在")

        # 过滤出有效的模型
        valid_models = [
            model for model in self.available_models
            if model["provider"] in selected_models
        ]

        if not valid_models:
            raise ValueError("没有选择有效的模型")

        # 获取下一个版本号
        next_version_number = self._get_next_version_number(db, proposal_id)

        # 为每个模型创建版本记录
        versions = []
        for model in valid_models:
            version = ProposalVersion(
                proposal_id=proposal_id,
                version_number=next_version_number,
                title=f"{proposal.title} - {model['name']}版本",
                customer_name=proposal.customer_name,
                customer_industry=proposal.customer_industry,
                customer_contact=proposal.customer_contact,
                model_provider=model["provider"],
                model_name=model["model"],
                status=ProposalVersionStatus.GENERATING,
                parent_version_id=parent_version_id,
                iteration_feedback=iteration_feedback,
                created_by=user_id,
                content={}  # 先创建空内容，生成完成后更新
            )
            db.add(version)
            db.flush()  # 获取ID
            versions.append(version)

        # 提交基础记录
        db.commit()

        # 并行生成方案内容
        generation_tasks = []
        for version, model in zip(versions, valid_models):
            task = self._generate_single_version(
                version, model, requirements, iteration_feedback, parent_version_id
            )
            generation_tasks.append(task)

        # 等待所有生成任务完成
        try:
            results = await asyncio.gather(*generation_tasks, return_exceptions=True)

            # 更新生成结果
            for i, (version, result) in enumerate(zip(versions, results)):
                if isinstance(result, Exception):
                    logger.error(f"版本 {version.id} 生成失败: {str(result)}")
                    version.status = ProposalVersionStatus.FAILED
                    version.changes_summary = f"生成失败: {str(result)}"
                else:
                    content, duration, tokens = result
                    version.content = content
                    version.generation_time = datetime.utcnow()
                    version.generation_duration = duration
                    version.tokens_used = tokens
                    version.status = ProposalVersionStatus.COMPLETED
                    version.changes_summary = f"使用{model['name']}生成"

                db.add(version)

            db.commit()
            return versions

        except Exception as e:
            logger.error(f"批量生成失败: {str(e)}")
            # 标记所有版本为失败
            for version in versions:
                version.status = ProposalVersionStatus.FAILED
                version.changes_summary = f"批量生成失败: {str(e)}"
                db.add(version)
            db.commit()
            raise

    async def _generate_single_version(
        self,
        version: ProposalVersion,
        model: Dict,
        requirements: str,
        iteration_feedback: Optional[str],
        parent_version_id: Optional[int]
    ) -> Tuple[Dict, int, int]:
        """
        生成单个版本的方案内容

        Returns:
            (content_dict, duration_seconds, tokens_used)
        """
        start_time = time.time()

        # 构建提示词
        prompt = self._build_generation_prompt(
            requirements, iteration_feedback, parent_version_id
        )

        try:
            # 切换到指定模型
            ai_service.provider = model["provider"]
            logger.info(f"开始使用 {model['name']} 生成方案版本 {version.id}")

            # 生成方案
            full_content = await ai_service.generate_text(
                prompt, temperature=0.7, max_tokens=4000
            )

            # 解析内容为结构化格式
            content_dict = await self._parse_generated_content(full_content, version)

            duration = int(time.time() - start_time)
            tokens = len(full_content.split())  # 简单估算

            logger.info(f"完成版本 {version.id} 生成，耗时 {duration} 秒")
            return content_dict, duration, tokens

        except Exception as e:
            logger.error(f"版本 {version.id} 生成异常: {str(e)}")
            raise

    def _build_generation_prompt(
        self,
        requirements: str,
        iteration_feedback: Optional[str],
        parent_version_id: Optional[int]
    ) -> str:
        """构建生成提示词"""
        base_prompt = f"""
作为专业的金融售前方案专家，请基于以下客户需求生成一份详细的技术方案：

客户需求：
{requirements}

请生成包含以下结构的完整方案：
1. 执行摘要
2. 解决方案概述
3. 技术架构设计
4. 实施计划
5. 预期效果
6. 风险评估

方案要求：
- 专业、具体、可执行
- 体现金融行业特点
- 结构清晰、逻辑严谨
- 字数控制在2000-3000字
"""

        if iteration_feedback and parent_version_id:
            base_prompt += f"""

用户反馈与迭代要求：
{iteration_feedback}

请基于以上反馈，对上一版本方案进行改进和优化，重点关注用户提出的具体要求。
"""

        return base_prompt

    async def _parse_generated_content(self, full_content: str, version: ProposalVersion) -> Dict:
        """
        解析生成的内容为结构化格式
        """
        try:
            # 使用现有的提案生成器来解析内容
            structured_content = await proposal_generator._parse_proposal_content(full_content)

            # 添加版本特定信息
            structured_content.update({
                "requirements": full_content[:500] + "..." if len(full_content) > 500 else full_content,
                "full_content": full_content,
                "generation_metadata": {
                    "model_provider": version.model_provider,
                    "model_name": version.model_name,
                    "version_number": version.version_number,
                    "generated_at": datetime.utcnow().isoformat()
                }
            })

            return structured_content

        except Exception as e:
            logger.warning(f"内容解析失败，使用简单结构: {str(e)}")
            # 如果解析失败，使用简单的结构
            return {
                "requirements": full_content[:500] + "..." if len(full_content) > 500 else full_content,
                "executive_summary": full_content[:300] + "..." if len(full_content) > 300 else full_content,
                "solution_overview": full_content,
                "technical_details": "",
                "implementation_plan": "",
                "full_content": full_content,
                "generation_metadata": {
                    "model_provider": version.model_provider,
                    "model_name": version.model_name,
                    "version_number": version.version_number,
                    "generated_at": datetime.utcnow().isoformat(),
                    "parse_error": str(e)
                }
            }

    def _get_next_version_number(self, db: Session, proposal_id: int) -> int:
        """获取下一个版本号"""
        latest_version = db.query(ProposalVersion)\
            .filter(ProposalVersion.proposal_id == proposal_id)\
            .order_by(ProposalVersion.version_number.desc())\
            .first()

        if latest_version:
            return latest_version.version_number + 1
        return 1

    async def iterate_proposal_version(
        self,
        db: Session,
        version_id: int,
        feedback: str,
        selected_models: List[str],
        user_id: int
    ) -> List[ProposalVersion]:
        """
        基于反馈迭代生成新的方案版本

        Args:
            db: 数据库会话
            version_id: 要迭代的版本ID
            feedback: 用户反馈
            selected_models: 选择使用的模型
            user_id: 用户ID

        Returns:
            新生成的版本列表
        """
        # 获取原版本
        original_version = db.query(ProposalVersion).filter(ProposalVersion.id == version_id).first()
        if not original_version:
            raise ValueError(f"版本 {version_id} 不存在")

        # 获取方案信息
        proposal = db.query(Proposal).filter(Proposal.id == original_version.proposal_id).first()

        # 构建需求描述
        requirements = proposal.requirements or ""
        if original_version.content and isinstance(original_version.content, dict):
            requirements = original_version.content.get("requirements", requirements)

        # 生成新版本
        new_versions = await self.generate_proposal_versions(
            db=db,
            proposal_id=original_version.proposal_id,
            selected_models=selected_models,
            requirements=requirements,
            user_id=user_id,
            iteration_feedback=feedback,
            parent_version_id=version_id
        )

        # 更新原版本的迭代反馈
        original_version.iteration_feedback = feedback
        db.add(original_version)
        db.commit()

        return new_versions

    def get_available_models(self) -> List[Dict]:
        """获取可用的AI模型列表"""
        return self.available_models.copy()

    async def compare_versions(
        self,
        db: Session,
        version_ids: List[int]
    ) -> Dict:
        """
        比较多个版本的内容

        Args:
            db: 数据库会话
            version_ids: 要比较的版本ID列表

        Returns:
            比较结果字典
        """
        versions = db.query(ProposalVersion)\
            .filter(ProposalVersion.id.in_(version_ids))\
            .all()

        if not versions:
            raise ValueError("没有找到要比较的版本")

        comparison = {
            "versions": [],
            "comparison_summary": {}
        }

        for version in versions:
            version_data = version.to_dict()
            # 移除完整内容以减少传输量
            if "content" in version_data and isinstance(version_data["content"], dict):
                content_summary = {
                    "executive_summary": version_data["content"].get("executive_summary", "")[:200],
                    "solution_overview": version_data["content"].get("solution_overview", "")[:200],
                    "key_points": version_data["content"].get("key_points", []),
                    "estimated_duration": version_data["content"].get("estimated_duration", ""),
                    "estimated_cost": version_data["content"].get("estimated_cost", "")
                }
                version_data["content_summary"] = content_summary
                del version_data["content"]

            comparison["versions"].append(version_data)

        # 生成对比摘要
        comparison["comparison_summary"] = self._generate_comparison_summary(versions)

        return comparison

    def _generate_comparison_summary(self, versions: List[ProposalVersion]) -> Dict:
        """生成版本对比摘要"""
        if len(versions) < 2:
            return {"message": "需要至少2个版本进行对比"}

        models_used = [f"{v.model_provider}({v.model_name})" for v in versions]
        status_counts = {}
        for v in versions:
            status = v.status.value if v.status else "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

        avg_tokens = sum(v.tokens_used or 0 for v in versions) // len(versions)
        avg_duration = sum(v.generation_duration or 0 for v in versions) // len(versions)

        return {
            "total_versions": len(versions),
            "models_used": models_used,
            "status_distribution": status_counts,
            "average_tokens": avg_tokens,
            "average_generation_duration": avg_duration,
            "version_range": f"v{min(v.version_number for v in versions)} - v{max(v.version_number for v in versions)}"
        }


# 全局实例
multi_model_proposal_service = MultiModelProposalService()