"""
Prometheus 指标监控
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# AI 调用指标
ai_calls_total = Counter("ai_calls_total", "Total number of AI calls", ["provider", "model", "status"])

ai_calls_duration = Histogram("ai_calls_duration_seconds", "AI call duration in seconds", ["provider", "model"])

ai_tokens_used = Counter("ai_tokens_used_total", "Total tokens used", ["provider", "model"])

# 向量搜索指标
vector_search_total = Counter("vector_search_total", "Total number of vector searches", ["collection", "status"])

vector_search_duration = Histogram(
    "vector_search_duration_seconds", "Vector search duration in seconds", ["collection"]
)

# Cache 指标
cache_operations_total = Counter(
    "cache_operations_total", "Total cache operations", ["operation", "cache_type", "status"]
)

cache_hit_rate = Gauge("cache_hit_rate", "Cache hit rate", ["cache_type"])

# HTTP 请求指标
http_requests_total = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])

http_request_duration = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])

# 当前活跃连接数
active_connections = Gauge("active_connections", "Number of active connections")


def track_ai_metrics(provider: str, model: str):
    """AI调用指标追踪装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise e
            finally:
                duration = time.time() - start_time
                ai_calls_total.labels(provider=provider, model=model, status=status).inc()
                ai_calls_duration.labels(provider=provider, model=model).observe(duration)

        return wrapper

    return decorator


def track_vector_search_metrics(collection: str):
    """向量搜索指标追踪装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise e
            finally:
                duration = time.time() - start_time
                vector_search_total.labels(collection=collection, status=status).inc()
                vector_search_duration.labels(collection=collection).observe(duration)

        return wrapper

    return decorator


def track_cache_metrics(cache_type: str, operation: str):
    """缓存操作指标追踪装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise e
            finally:
                cache_operations_total.labels(cache_type=cache_type, operation=operation, status=status).inc()

        return wrapper

    return decorator


def update_cache_hit_rate(cache_type: str, hits: int, total: int):
    """更新缓存命中率"""
    if total > 0:
        rate = hits / total
        cache_hit_rate.labels(cache_type=cache_type).set(rate)


def get_metrics():
    """获取所有指标"""
    return generate_latest()


def counter_total(counter: Counter) -> float:
    """获取Counter的总值"""
    total = 0.0
    for metric in counter.collect():
        for sample in metric.samples:
            total += float(sample.value)
    return total
