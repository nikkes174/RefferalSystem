from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "detail": str(e),
                    "correlation_id": request.state.correlation_id,
                },
            )

        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "detail": "Internal server error",
                    "correlation_id": request.state.correlation_id,
                },
            )
