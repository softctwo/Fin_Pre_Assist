"""
缓存服务 - Redis + 内存回退

提供统一的缓存接口，支持Redis和内存两种缓存方式
"""
import json
import hashlib
from typing import Any, Optional, Dict
from loguru import logger

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis-asyncio未安装，将使用内存缓存")

from app.core.config import settings


class CacheService:
    """统一缓存服务"""
    
    def __init__(self):
        """初始化缓存服务"""
        self._redis_client = None
        self._memory_cache = {}
        self._cache_type = "memory"
        self._hits = 0
        self._misses = 0
        
        if REDIS_AVAILABLE:
            try:
                self._init_redis()
            except Exception as e:
                logger.error(f"Redis初始化失败: {e}，使用内存缓存")
    
    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self._cache_type = "redis"
            logger.info("✅ Redis缓存服务初始化成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self._redis_client = None
            self._cache_type = "memory"
    
    def _generate_key(self, key: str, prefix: str = "") -> str:
        """生成缓存键，长键使用MD5哈希"""
        full_key = f"{prefix}:{key}" if prefix else key
        
        # 如果键太长，使用MD5哈希
        if len(full_key) > 200:
            hash_key = hashlib.md5(full_key.encode()).hexdigest()
            return f"{prefix}:hash_{hash_key}"
        
        return full_key
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存"""
        try:
            value_str = json.dumps(value, ensure_ascii=False)
            
            if self._cache_type == "redis" and self._redis_client:
                try:
                    await self._redis_client.setex(key, ttl, value_str)
                    return True
                except Exception as e:
                    logger.warning(f"Redis set失败: {e}，降级到内存缓存")
                    self._memory_cache[key] = value
                    return True
            else:
                self._memory_cache[key] = value
                return True
                
        except Exception as e:
            logger.error(f"缓存set失败: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            if self._cache_type == "redis" and self._redis_client:
                try:
                    value_str = await self._redis_client.get(key)
                    if value_str:
                        self._hits += 1
                        return json.loads(value_str)
                    else:
                        self._misses += 1
                        return None
                except Exception as e:
                    logger.warning(f"Redis get失败: {e}，尝试内存缓存")
                    value = self._memory_cache.get(key)
                    if value:
                        self._hits += 1
                    else:
                        self._misses += 1
                    return value
            else:
                value = self._memory_cache.get(key)
                if value:
                    self._hits += 1
                else:
                    self._misses += 1
                return value
                
        except Exception as e:
            logger.error(f"缓存get失败: {e}")
            self._misses += 1
            return None
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            if self._cache_type == "redis" and self._redis_client:
                try:
                    return await self._redis_client.exists(key) > 0
                except Exception:
                    return key in self._memory_cache
            else:
                return key in self._memory_cache
        except Exception as e:
            logger.error(f"缓存exists失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self._cache_type == "redis" and self._redis_client:
                try:
                    await self._redis_client.delete(key)
                except Exception:
                    pass
            
            if key in self._memory_cache:
                del self._memory_cache[key]
            
            return True
        except Exception as e:
            logger.error(f"缓存delete失败: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有键"""
        deleted_count = 0
        
        try:
            if self._cache_type == "redis" and self._redis_client:
                try:
                    cursor = 0
                    while True:
                        cursor, keys = await self._redis_client.scan(
                            cursor=cursor,
                            match=pattern,
                            count=100
                        )
                        if keys:
                            deleted_count += await self._redis_client.delete(*keys)
                        if cursor == 0:
                            break
                except Exception as e:
                    logger.warning(f"Redis clear_pattern失败: {e}")
            
            # 清理内存缓存
            if pattern == "*":
                deleted_count += len(self._memory_cache)
                self._memory_cache.clear()
            else:
                # 简单的模式匹配
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                deleted_count += len(keys_to_delete)
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return deleted_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "type": self._cache_type,
            "status": "enabled",
            "keys": 0,
            "memory_used": "N/A",
            "hit_rate": "0.00%",
            "total_requests": self._hits + self._misses,
            "hits": self._hits,
            "misses": self._misses
        }
        
        try:
            if self._cache_type == "redis" and self._redis_client:
                try:
                    # 获取键数量
                    stats["keys"] = await self._redis_client.dbsize()
                    
                    # 获取内存信息
                    info = await self._redis_client.info("memory")
                    memory_bytes = info.get("used_memory", 0)
                    stats["memory_used"] = self._format_bytes(memory_bytes)
                except Exception as e:
                    logger.warning(f"获取Redis统计失败: {e}")
            else:
                stats["keys"] = len(self._memory_cache)
                stats["memory_used"] = "内存缓存"
            
            # 计算命中率
            total = self._hits + self._misses
            if total > 0:
                hit_rate = (self._hits / total) * 100
                stats["hit_rate"] = f"{hit_rate:.2f}%"
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
        
        return stats
    
    def _format_bytes(self, bytes_value: int) -> str:
        """格式化字节数"""
        for unit in ['B', 'K', 'M', 'G']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f}{unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f}T"
    
    # ==================== 业务专用方法 ====================
    
    async def cache_ai_response(
        self,
        prompt: str,
        response: str,
        expire: int = 3600
    ) -> bool:
        """缓存AI响应"""
        key = self._generate_key(prompt, "ai_response")
        return await self.set(key, response, ttl=expire)
    
    async def get_ai_response(self, prompt: str) -> Optional[str]:
        """获取缓存的AI响应"""
        key = self._generate_key(prompt, "ai_response")
        return await self.get(key)
    
    async def cache_vector_search(
        self,
        query: str,
        collection: str,
        results: list,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None,
        expire: int = 1800
    ) -> bool:
        """缓存向量搜索结果"""
        # 生成唯一键
        key_data = {
            "query": query,
            "collection": collection,
            "n_results": n_results,
            "filter": filter_metadata
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key = self._generate_key(key_str, f"vector_search:{collection}")
        return await self.set(key, results, ttl=expire)
    
    async def get_vector_search(
        self,
        query: str,
        collection: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Optional[list]:
        """获取缓存的向量搜索结果"""
        key_data = {
            "query": query,
            "collection": collection,
            "n_results": n_results,
            "filter": filter_metadata
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key = self._generate_key(key_str, f"vector_search:{collection}")
        return await self.get(key)
    
    async def invalidate_vector_cache(self, collection: str) -> int:
        """失效指定集合的所有向量搜索缓存"""
        pattern = f"vector_search:{collection}:*"
        return await self.clear_pattern(pattern)
    
    async def cache_proposal_list(
        self,
        user_id: int,
        filters: Dict,
        proposals: Any,
        expire: int = 300
    ) -> bool:
        """缓存方案列表"""
        key_data = {
            "user_id": user_id,
            "filters": filters
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key = self._generate_key(key_str, "proposal_list")
        
        # 如果proposals包含模型对象，尝试转换
        try:
            if hasattr(proposals, "__dict__"):
                # 单个对象
                proposals_data = self._model_to_dict(proposals)
            elif isinstance(proposals, dict):
                # 字典（可能包含items列表）
                proposals_data = proposals.copy()
                if "items" in proposals_data:
                    proposals_data["items"] = [
                        self._model_to_dict(item) if hasattr(item, "__dict__") else item
                        for item in proposals_data["items"]
                    ]
            else:
                proposals_data = proposals
            
            return await self.set(key, proposals_data, ttl=expire)
        except Exception as e:
            logger.warning(f"缓存方案列表失败: {e}")
            return False
    
    async def get_proposal_list(
        self,
        user_id: int,
        filters: Dict
    ) -> Optional[Any]:
        """获取缓存的方案列表"""
        key_data = {
            "user_id": user_id,
            "filters": filters
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key = self._generate_key(key_str, "proposal_list")
        return await self.get(key)
    
    async def invalidate_user_proposals(self, user_id: int) -> int:
        """失效用户的所有方案列表缓存"""
        pattern = f"proposal_list:*user_id*{user_id}*"
        return await self.clear_pattern(pattern)
    
    def _model_to_dict(self, model) -> dict:
        """将SQLAlchemy模型转换为字典"""
        if hasattr(model, "__dict__"):
            result = {}
            for key, value in model.__dict__.items():
                if not key.startswith("_"):
                    # 处理特殊类型
                    if hasattr(value, "isoformat"):  # datetime
                        result[key] = value.isoformat()
                    elif hasattr(value, "value"):  # Enum
                        result[key] = value.value
                    else:
                        result[key] = value
            return result
        return model


# 全局单例
cache_service = CacheService()
