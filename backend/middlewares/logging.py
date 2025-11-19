import json
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        cid = getattr(request.state, "correlation_id", None)

        response = await call_next(request)

        log = {
            "correlation_id": cid,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": round(time.time() - start, 4),
        }

        print(json.dumps(log, ensure_ascii=False))
        return response
