"""Request metrics middleware."""

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    http_requests_total,
    http_request_duration,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that records request duration and status code."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        start = time.perf_counter()
        method = request.method
        path = request.url.path
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=str(status_code),
            ).inc()
            http_request_duration.labels(
                method=method,
                endpoint=path,
            ).observe(duration)
