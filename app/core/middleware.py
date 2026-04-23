import time
import uuid
from typing import Callable

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 尝试从请求头获取 Trace ID，如果没有则生成一个
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())

        # 将 trace_id 绑定到当前上下文中，后续所有的 logger 都会附带此信息
        with logger.contextualize(trace_id=trace_id):
            start_time = time.time()

            # 获取请求的真实 IP 和请求路径
            client_ip = request.client.host if request.client else "Unknown"
            logger.info(
                "Incoming Request | {} {} | IP: {}",
                request.method,
                request.url.path,
                client_ip,
            )

            try:
                response = await call_next(request)
            except Exception as e:
                # 记录全局异常
                process_time = time.time() - start_time
                logger.exception(
                    "Request Failed | {} {} | error: {} | {:.3f}s",
                    request.method,
                    request.url.path,
                    str(e),
                    process_time,
                )
                raise e
            finally:
                pass

            process_time = time.time() - start_time
            logger.info(
                "Request Completed | {} {} | Status: {} | {:.3f}s",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )

            # 为前端回传 Trace ID，方便跨域调试
            response.headers["X-Trace-Id"] = trace_id
            return response
