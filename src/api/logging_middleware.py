from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from utility.logging import get_logger


request_logger = get_logger("requests", "requests.log")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            request_logger.error(
                f"{request.method} {request.url.path} "
                f"completed_in={process_time:.2f}ms status_code=500"
            )
            raise exc
        process_time = (time.time() - start_time) * 1000
        log_msg = (f"{request.method} {request.url.path} "
                   f"completed_in={process_time:.2f}ms "
                   f"status_code={response.status_code}")
        
        if response.status_code >= 500:
            request_logger.error(log_msg)
        elif response.status_code >= 400:
            request_logger.warning(log_msg)
        else:
            request_logger.info(log_msg)
        return response
