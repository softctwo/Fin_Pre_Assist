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
from app.models.ai_model import AIModel
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类 - 支持多模型配置"""

    def __init__(self, model_config: Optional[AIModel] = None):
        self._model_config = model_config
        self._provider = None
        self._model_name = None
        self._wenxin_token: Optional[str] = None
        self._wenxin_token_expire: float = 0
        self._system_prompt = "你是一个专业的金融行业售前方案专家，擅长撰写技术方案和商务文档。"
        self._http_timeout = 120
        self.client = None
        
        if model_config:
            self._load_model_config(model_config)
        else:
            self._load_default_config()
        self._initialize_client()
    
    def _load_model_config(self, config: AIModel):
        """从数据库配置加载模型设置"""
        self._model_config = config
        self._provider = config.provider.lower()
        self._model_name = config.model_name
        self._http_timeout = config.timeout
        self._max_tokens = config.max_tokens
        self._temperature = config.temperature
        self._top_p = config.top_p
        self._frequency_penalty = config.frequency_penalty
        self._presence_penalty = config.presence_penalty
        self._base_url = config.base_url
        self._api_key = config.api_key
        self._headers = config.headers or {}
        self._extra_params = config.extra_params or {}
    
    def _load_default_config(self):
        """从环境变量加载默认配置"""
        self._provider = (settings.AI_PROVIDER or "openai").lower()
        self._model_name = getattr(settings, f"{self._provider.upper()}_MODEL", "gpt-3.5-turbo")
        self._http_timeout = 120
        self._max_tokens = 2000
        self._temperature = 0.7
        self._top_p = 1.0
        self._frequency_penalty = 0.0
        self._presence_penalty = 0.0
        self._base_url = None
        self._api_key = None
        self._headers = {}
        self._extra_params = {}

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
            
            api_key = self._api_key or settings.OPENAI_API_KEY
            base_url = self._base_url or "https://api.openai.com/v1"
            
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self._http_timeout
            )
            
        elif self.provider == "zhipu":
            # Zhipu uses a custom client, handled in the method
            pass
        elif self.provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API
            if openai is None:
                raise RuntimeError("openai package is not installed")
                
            api_key = self._api_key or settings.DEEPSEEK_API_KEY
            base_url = self._base_url or "https://api.deepseek.com/v1"
            
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self._http_timeout
            )
        elif self.provider == "kimi":
            # Kimi uses a custom client, handled in the method
            pass
        elif self.provider == "tongyi":
            if dashscope is None:
                raise RuntimeError("dashscope package is not installed")
            dashscope.api_key = self._api_key or settings.TONGYI_API_KEY
        elif self.provider == "wenxin":
            if erniebot is None:
                raise RuntimeError("erniebot package is not installed")
            erniebot.api_type = "aistudio"
            erniebot.access_token = self._api_key or settings.WENXIN_API_KEY

    async def generate_text(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """生成文本"""
        model_name = self._model_name
        start_time = time.time()
        tokens_used = 0
        status = "success"
        
        # 使用配置参数，如果未提供则使用模型默认值
        temp = temperature if temperature is not None else self._temperature
        tokens = max_tokens if max_tokens is not None else self._max_tokens

        try:
            if self.provider == "openai":
                text, tokens_used = await self._generate_with_openai(prompt, temp, tokens)
            elif self.provider == "tongyi":
                text, tokens_used = await self._generate_with_tongyi(prompt, temp, tokens)
            elif self.provider == "wenxin":
                text, tokens_used = await self._generate_with_wenxin(prompt, temp, tokens)
            elif self.provider == "zhipu":
                text, tokens_used = await self._generate_with_zhipu(prompt, temp, tokens)
            elif self.provider == "deepseek":
                text, tokens_used = await self._generate_with_deepseek(prompt, temp, tokens)
            elif self.provider == "kimi":
                text, tokens_used = await self._generate_with_kimi(prompt, temp, tokens)
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
        if not self.client:
            raise RuntimeError("OpenAI客户端未初始化")

        try:
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=self._build_messages(prompt),
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self._top_p,
                frequency_penalty=self._frequency_penalty,
                presence_penalty=self._presence_penalty,
                **self._extra_params
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

        # 智谱AI API的最新格式
        payload = {
            "model": settings.ZHIPU_MODEL,
            "messages": self._build_messages(prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "top_p": 0.7,
        }

        # 智谱AI API认证 - 支持多种格式
        headers = {
            "Content-Type": "application/json"
        }

        # 智谱AI API密钥格式检查
        api_key = settings.ZHIPU_API_KEY

        # 如果API密钥包含点号，可能是新的格式
        if "." in api_key:
            # 尝试使用Bearer token格式
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            # 备用认证方式
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                response = await client.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    json=payload,
                    headers=headers
                )

                # 检查响应状态
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    raise Exception(f"智谱AI API请求失败 (状态码: {response.status_code}): {error_data}")

                data = response.json()

            # 检查智谱AI的错误响应格式
            if "error" in data:
                error_msg = data["error"].get("message", "未知错误")
                error_code = data["error"].get("code", "UNKNOWN_ERROR")
                raise Exception(f"智谱AI调用失败 [{error_code}]: {error_msg}")

            # 解析正常的响应
            try:
                message = data["choices"][0]["message"]
                # 智谱AI某些模型可能使用不同的字段名
                text = message.get("content", "")

                # 如果content为空，检查其他可能的字段
                if not text:
                    text = message.get("reasoning_content", "") or message.get("text", "")

                text = text.strip()

                # 获取token使用情况
                usage = data.get("usage", {})
                tokens = int(usage.get("total_tokens", 0) or 0)

                if not text:
                    raise Exception("智谱AI返回了空的内容")

                return text, tokens

            except (KeyError, IndexError) as exc:
                logger.error(f"智谱AI响应解析失败: {data}")
                raise Exception(f"智谱AI响应格式异常: 缺少必要字段") from exc

        except httpx.TimeoutException:
            raise Exception("智谱AI API请求超时")
        except httpx.NetworkError as e:
            raise Exception(f"智谱AI网络连接错误: {str(e)}")
        except Exception as e:
            if isinstance(e, Exception) and "智谱AI" in str(e):
                raise
            logger.exception("智谱AI调用发生未知错误:")
            raise Exception(f"智谱AI调用失败: {str(e)}")

    async def _generate_with_deepseek(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用DeepSeek生成文本"""
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未配置")

        payload = {
            "model": settings.DEEPSEEK_MODEL,
            "messages": self._build_messages(prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

        try:
            message = data["choices"][0]["message"]
            text = message.get("content", "")
            text = text.strip()
            tokens = int(data.get("usage", {}).get("total_tokens", 0) or 0)
            return text, tokens
        except (KeyError, IndexError) as exc:
            if "error" in data:
                raise Exception(f"DeepSeek调用失败: {data['error'].get('message')}")
            raise Exception(f"DeepSeek响应格式异常: {data}") from exc

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
        # 向量模型配置：优先使用zhipu，确保稳定性
        if self.provider == "kimi":
            # Kimi文本生成时，向量仍使用zhipu确保稳定性
            logger.info("Kimi模式下使用zhipu进行向量化")
            return await self._zhipu_embed_text(text)
        elif self.provider == "openai":
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
        elif self.provider == "deepseek":
            return await self._deepseek_embed_text(text)
        else:
            raise NotImplementedError(f"{self.provider}的向量化待实现")

    async def _zhipu_embed_text(self, text: str) -> List[float]:
        """使用智谱AI进行文本向量化"""
        if not settings.ZHIPU_API_KEY:
            raise ValueError("ZHIPU_API_KEY 未配置")

        url = "https://open.bigmodel.cn/api/paas/v4/embeddings"

        payload = {
            "model": settings.ZHIPU_EMBEDDING_MODEL,
            "input": text,
            "encoding_format": "float"
        }

        # 使用与文本生成相同的认证方式
        api_key = settings.ZHIPU_API_KEY
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                response = await client.post(url, json=payload, headers=headers)

                # 检查响应状态
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                    raise Exception(f"智谱AI Embedding API请求失败 (状态码: {response.status_code}): {error_data}")

                data = response.json()

            # 检查智谱AI的错误响应格式
            if "error" in data:
                error_msg = data["error"].get("message", "未知错误")
                error_code = data["error"].get("code", "UNKNOWN_ERROR")
                raise Exception(f"智谱AI Embedding调用失败 [{error_code}]: {error_msg}")

            # 解析正常的响应
            try:
                embedding = data["data"][0]["embedding"]
                return embedding
            except (KeyError, IndexError) as exc:
                logger.error(f"智谱AI Embedding响应解析失败: {data}")
                raise Exception(f"智谱AI Embedding响应格式异常: 缺少必要字段") from exc

        except httpx.TimeoutException:
            raise Exception("智谱AI Embedding API请求超时")
        except httpx.NetworkError as e:
            raise Exception(f"智谱AI Embedding网络连接错误: {str(e)}")
        except Exception as e:
            if isinstance(e, Exception) and "智谱AI" in str(e):
                raise
            logger.exception("智谱AI Embedding调用发生未知错误:")
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

    async def _deepseek_embed_text(self, text: str) -> List[float]:
        """使用DeepSeek进行文本向量化"""
        # DeepSeek目前没有专门的embedding API，我们可以使用OpenAI兼容的embedding接口
        # 或者使用其他替代方案，暂时使用一个基本的实现
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未配置")

        payload = {
            "model": "text-embedding-ada-002",  # 使用标准的embedding模型
            "input": text,
            "encoding_format": "float"
        }
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/embeddings",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            embedding = data["data"][0]["embedding"]
            return embedding
        except Exception as e:
            # 如果DeepSeek不支持embedding，fallback到OpenAI或使用简单的实现
            logger.warning(f"DeepSeek向量化失败，使用简单实现: {str(e)}")
            # 简单的文本向量化实现（仅用于演示）
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # 将字节转换为浮点数向量
            embedding = [float(b) / 255.0 for b in hash_bytes[:128]]
            # 如果长度不够，用0填充
            if len(embedding) < 128:
                embedding.extend([0.0] * (128 - len(embedding)))
            return embedding

    async def _generate_with_kimi(self, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, int]:
        """使用Kimi生成文本"""
        if not settings.KIMI_API_KEY:
            raise ValueError("KIMI_API_KEY 未配置")

        payload = {
            "model": settings.KIMI_MODEL,
            "messages": self._build_messages(prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {settings.KIMI_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self._http_timeout) as client:
                response = await client.post(
                    f"{settings.KIMI_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            try:
                message = data["choices"][0]["message"]
                text = message.get("content", "")
                text = text.strip()
                tokens = int(data.get("usage", {}).get("total_tokens", 0) or 0)

                if not text:
                    raise Exception("Kimi返回了空的内容")

                return text, tokens

            except (KeyError, IndexError) as exc:
                logger.error(f"Kimi响应解析失败: {data}")
                raise Exception(f"Kimi响应格式异常: 缺少必要字段") from exc

        except httpx.TimeoutException:
            raise Exception("Kimi API请求超时")
        except httpx.NetworkError as e:
            raise Exception(f"Kimi网络连接错误: {str(e)}")
        except Exception as e:
            if isinstance(e, Exception) and "Kimi" in str(e):
                raise
            logger.exception("Kimi调用发生未知错误:")
            raise Exception(f"Kimi调用失败: {str(e)}")

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
        if self.provider == "deepseek":
            return settings.DEEPSEEK_MODEL
        if self.provider == "kimi":
            return settings.KIMI_MODEL
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
