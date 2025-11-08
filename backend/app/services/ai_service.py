from typing import Optional, List, Tuple
import asyncio
import time
import httpx
import numpy as np

try:
    import openai
except ImportError:
    openai = None

try:
    import dashscope
except ImportError:
    dashscope = None

try:
    import erniebot
except ImportError:
    erniebot = None

from app.core.config import settings
from app.core.metrics import ai_calls_total, ai_calls_duration, ai_tokens_used


class AIService:
    """AI服务类 - 封装各种AI模型接口"""

    def __init__(self):
        self._provider = (settings.AI_PROVIDER or "openai").lower()
        self.model = settings.OPENAI_MODEL
        self._wenxin_token: Optional[str] = None
        self._wenxin_token_expire: float = 0
        self._system_prompt = "你是一个专业的金融行业售前方案专家，擅长撰写技术方案和商务文档。"
        self._http_timeout = 30
        self.client = None
        self._initialize_client()

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, value):
        self._provider = value.lower()
        self._initialize_client()

    def _initialize_client(self):
        if self.provider == "openai":
            if openai is None:
                raise RuntimeError("openai package is not installed")
            openai.api_key = settings.OPENAI_API_KEY
            self.client = None
        elif self.provider == "zhipu":
            # Zhipu uses a custom client, handled in the method
            pass
        elif self.provider == "tongyi":
            if dashscope is None:
                raise RuntimeError("dashscope package is not installed")
            dashscope.api_key = settings.TONGYI_API_KEY
        elif self.provider == "wenxin":
            if erniebot is None:
                raise RuntimeError("erniebot package is not installed")
            erniebot.api_type = "aistudio"
            erniebot.access_token = settings.WENXIN_API_KEY

    async def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """生成文本"""
        model_name = self._resolve_model()
        start_time = time.time()
        tokens_used = 0
        status = "success"

        try:
            if self.provider == "openai":
                text, tokens_used = await self._generate_with_openai(prompt, temperature, max_tokens)
            elif self.provider == "tongyi":
                text, tokens_used = await self._generate_with_tongyi(prompt, temperature, max_tokens)
            elif self.provider == "wenxin":
                text, tokens_used = await self._generate_with_wenxin(prompt, temperature, max_tokens)
            elif self.provider == "zhipu":
                text, tokens_used = await self._generate_with_zhipu(prompt, temperature, max_tokens)
            else:
                raise ValueError(f"不支持的AI提供商: {self.provider}")
            return text
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            ai_calls_total.labels(provider=self.provider, model=model_name, status=status).inc()
            ai_calls_duration.labels(provider=self.provider, model=model_name).observe(duration)
            if tokens_used:
                ai_tokens_used.labels(provider=self.provider, model=model_name).inc(tokens_used)

    async def _generate_with_openai(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用OpenAI生成文本"""
        if openai is None:
            raise RuntimeError("openai package is not installed")

        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model, messages=self._build_messages(prompt), temperature=temperature, max_tokens=max_tokens
            )
            text = response.choices[0].message.content.strip()
            tokens = _extract_usage_tokens(getattr(response, "usage", None))
            return text, tokens
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")

    async def _generate_with_tongyi(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用通义千问生成文本"""
        if not settings.TONGYI_API_KEY:
            raise ValueError("TONGYI_API_KEY 未配置")
        if dashscope is None:
            raise RuntimeError("dashscope package is not installed")

        response = dashscope.Generation.call(
            model=settings.TONGYI_MODEL,
            messages=self._build_messages(prompt),
            result_format="message",
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if response.status_code == 200:
            try:
                choices = response.output.choices
                message = choices[0].message
                content = message.get("content")
                if isinstance(content, list):
                    text = "".join(item.get("text", "") for item in content)
                else:
                    text = content or ""
                return text.strip(), int(response.usage.total_tokens or 0)
            except (KeyError, IndexError) as exc:
                raise Exception(f"通义千问响应格式异常: {response}") from exc
        else:
            raise Exception(f"通义千问API返回错误: {response.message}")

    async def _generate_with_wenxin(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用文心一言生成文本"""
        if not settings.WENXIN_API_KEY:
            raise ValueError("WENXIN_API_KEY 未配置")
        if erniebot is None:
            raise RuntimeError("erniebot package is not installed")

        response = erniebot.ChatCompletion.create(
            model=settings.WENXIN_MODEL,
            messages=self._build_messages(prompt),
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if hasattr(response, "result"):
            return response.result.strip(), int(response.usage.total_tokens or 0)
        if hasattr(response, "error_msg"):
            raise Exception(f"文心一言调用失败: {response.error_msg}")
        raise Exception(f"文心一言响应格式异常: {response}")

    async def _generate_with_zhipu(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用智谱AI生成文本"""
        if not settings.ZHIPU_API_KEY:
            raise ValueError("ZHIPU_API_KEY 未配置")

        payload = {
            "model": settings.ZHIPU_MODEL,
            "messages": self._build_messages(prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Authorization": f"Bearer {settings.ZHIPU_API_KEY}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions", json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()

        try:
            message = data["choices"][0]["message"]
            # glm-4.6等模型可能使用reasoning_content字段
            text = message.get("content", "") or message.get("reasoning_content", "")
            text = text.strip()
            tokens = int(data.get("usage", {}).get("total_tokens", 0) or 0)
            return text, tokens
        except (KeyError, IndexError) as exc:
            # 智谱错误通常包含 "error" 字段
            if "error" in data:
                raise Exception(f"智谱AI调用失败: {data['error'].get('message')}")
            raise Exception(f"智谱AI响应格式异常: {data}") from exc

    async def _get_wenxin_access_token(self) -> str:
        """获取或刷新文心一言访问令牌"""
        if self._wenxin_token and time.time() < self._wenxin_token_expire - 60:
            return self._wenxin_token

        if not (settings.WENXIN_API_KEY and settings.WENXIN_SECRET_KEY):
            raise ValueError("WENXIN_API_KEY 或 WENXIN_SECRET_KEY 未配置")

        params = {
            "grant_type": "client_credentials",
            "client_id": settings.WENXIN_API_KEY,
            "client_secret": settings.WENXIN_SECRET_KEY,
        }

        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.get("https://aip.baidubce.com/oauth/2.0/token", params=params)
            response.raise_for_status()
            data = response.json()

        if "access_token" not in data:
            raise Exception(f"获取文心一言token失败: {data}")

        self._wenxin_token = data["access_token"]
        expires_in = int(data.get("expires_in", 0))
        self._wenxin_token_expire = time.time() + expires_in
        return self._wenxin_token

    async def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        if self.provider == "openai":
            if openai is None:
                raise RuntimeError("openai package is not installed")
            try:
                response = await openai.Embedding.acreate(model="text-embedding-ada-002", input=text)
                data_section = response["data"] if isinstance(response, dict) else getattr(response, "data", None)
                if not data_section:
                    raise ValueError("OpenAI embedding response missing data field")
                first_entry = data_section[0]
                if isinstance(first_entry, dict):
                    return first_entry["embedding"]
                return first_entry.embedding
            except Exception as e:
                raise Exception(f"文本向量化失败: {str(e)}")
        elif self.provider == "zhipu":
            return await self._zhipu_embed_text(text)
        elif self.provider == "tongyi":
            return await self._tongyi_embed_text(text)
        elif self.provider == "wenxin":
            return await self._wenxin_embed_text(text)
        else:
            raise NotImplementedError(f"{self.provider}的向量化待实现")

    async def _zhipu_embed_text(self, text: str) -> List[float]:
        """使用智谱AI进行文本向量化"""
        if not settings.ZHIPU_API_KEY:
            raise ValueError("ZHIPU_API_KEY 未配置")

        url = "https://open.bigmodel.cn/api/paas/v4/embeddings"

        payload = {"model": settings.ZHIPU_EMBEDDING_MODEL, "input": text}

        headers = {"Authorization": f"Bearer {settings.ZHIPU_API_KEY}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            embedding = data["data"][0]["embedding"]
            return embedding
        except Exception as e:
            raise Exception(f"智谱AI向量化失败: {str(e)}")

    async def _tongyi_embed_text(self, text: str) -> List[float]:
        """使用通义千问进行文本向量化"""
        if dashscope is None:
            raise RuntimeError("dashscope package is not installed")
        resp = dashscope.TextEmbedding.call(model=settings.TONGYI_EMBEDDING_MODEL, input=text)
        if resp.status_code == 200:
            return resp.output["embeddings"][0]["embedding"]
        else:
            raise Exception(f"通义千问Embedding API返回错误: {resp.message}")

    async def _wenxin_embed_text(self, text: str) -> List[float]:
        """使用文心一言进行文本向量化"""
        if erniebot is None:
            raise RuntimeError("erniebot package is not installed")
        response = erniebot.Embedding.create(model=settings.WENXIN_EMBEDDING_MODEL, input=[text])
        if hasattr(response, "result"):
            return response.result[0]
        else:
            raise Exception(f"文心一言Embedding API返回错误: {response}")

    async def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[dict]:
        """语义搜索"""
        if not documents:
            return []

        query_vector = await self.embed_text(query)
        doc_vectors = await asyncio.gather(*(self.embed_text(doc) for doc in documents if doc))

        query_vector = np.array(query_vector)
        doc_vectors = np.array([v for v in doc_vectors if v])

        if doc_vectors.shape[0] == 0:
            return []

        # 计算余弦相似度
        similarities = np.dot(doc_vectors, query_vector) / (
            np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(query_vector)
        )

        # 获取top_k个最相似的文档
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]

        return [{"index": int(i), "score": float(similarities[i]), "text": documents[i]} for i in top_k_indices]

    def _build_messages(self, prompt: str) -> List[dict]:
        """构建通用的对话消息"""
        return [{"role": "system", "content": self._system_prompt}, {"role": "user", "content": prompt}]

    def _resolve_model(self) -> str:
        """获取当前provider使用的模型名称"""
        if self.provider == "openai":
            return settings.OPENAI_MODEL
        if self.provider == "tongyi":
            return settings.TONGYI_MODEL
        if self.provider == "wenxin":
            return settings.WENXIN_MODEL
        if self.provider == "zhipu":
            return settings.ZHIPU_MODEL
        return "unknown"


def _extract_usage_tokens(usage_obj: Optional[object]) -> int:
    """从OpenAI usage对象中提取token数量"""
    if usage_obj is None:
        return 0
    if isinstance(usage_obj, dict):
        return int(usage_obj.get("total_tokens", 0) or 0)
    return int(getattr(usage_obj, "total_tokens", 0) or 0)


# 全局实例
ai_service = AIService()
