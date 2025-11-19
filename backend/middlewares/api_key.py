from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

from backend.ExternalService.repository import ExternalServiceRepository
from backend.database.db import db


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix: str = "/api"):
        super().__init__(app)
        self.repo = ExternalServiceRepository()
        self.open_paths = {"/docs", "/openapi.json", "/health", "/redoc"}
        self.protected_prefix = protected_prefix

    async def dispatch(self, request, call_next):
        path = request.url.path

        # Разрешённые пути
        if path in self.open_paths:
            return await call_next(request)

        # Все пути, НЕ начинающиеся с protected_prefix → открытые
        if not path.startswith(self.protected_prefix):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse({"detail": "Missing API key"}, status_code=401)

        try:
            async for session in db.get_session():
                service = await self.repo.get_by_api_key(session, api_key)
                break
        except Exception as e:
            return JSONResponse({"detail": f"DB error: {e}"}, status_code=500)

        if not service:
            return JSONResponse({"detail": "Invalid API key"}, status_code=403)

        return await call_next(request)
