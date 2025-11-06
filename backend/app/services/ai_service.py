"""AI服务"""
from typing import Optional, List
import openai
from app.core.config import settings


class AIService:
    """AI服务类 - 封装各种AI模型接口"""

    def __init__(self):
        self.provider = settings.AI_PROVIDER

        if self.provider == "openai":
            openai.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """生成文本"""
        if self.provider == "openai":
            return await self._generate_with_openai(prompt, temperature, max_tokens)
        elif self.provider == "tongyi":
            return await self._generate_with_tongyi(prompt, temperature, max_tokens)
        elif self.provider == "wenxin":
            return await self._generate_with_wenxin(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"不支持的AI提供商: {self.provider}")

    async def _generate_with_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """使用OpenAI生成文本"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的金融行业售前方案专家，擅长撰写技术方案和商务文档。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")

    async def _generate_with_tongyi(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """使用通义千问生成文本"""
        # TODO: 实现通义千问接口
        raise NotImplementedError("通义千问接口待实现")

    async def _generate_with_wenxin(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """使用文心一言生成文本"""
        # TODO: 实现文心一言接口
        raise NotImplementedError("文心一言接口待实现")

    async def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        if self.provider == "openai":
            try:
                response = await openai.Embedding.acreate(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response['data'][0]['embedding']
            except Exception as e:
                raise Exception(f"文本向量化失败: {str(e)}")
        else:
            # TODO: 实现其他提供商的向量化
            raise NotImplementedError(f"{self.provider}的向量化待实现")

    async def semantic_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[int]:
        """语义搜索"""
        # TODO: 实现语义搜索功能
        # 1. 将query和documents都转换为向量
        # 2. 计算相似度
        # 3. 返回top_k个最相似的文档索引
        raise NotImplementedError("语义搜索功能待实现")
