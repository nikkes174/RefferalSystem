from fastapi import FastAPI

from backend.ExternalService.router import router as external_service_router
from backend.User.router import router as user_router
from backend.Referral.routers import router as referral_router
from backend.ReferralCode.routers import router as referral_code_router

from backend.middlewares.api_key import ApiKeyMiddleware
from backend.middlewares.correlation import CorrelationIdMiddleware
from backend.middlewares.logging import LoggingMiddleware
from backend.middlewares.errors import ErrorHandlerMiddleware


app = FastAPI(title="ReferralSystem")

# FIX: порядок объявления обратен порядку выполнения
app.add_middleware(ApiKeyMiddleware)            # должен выполняться ПОСЛЕДНИМ
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)     # должен выполняться ПЕРВЫМ

# подключаем роутеры ПОСЛЕ всех middleware
app.include_router(external_service_router)
app.include_router(user_router)
app.include_router(referral_router)
app.include_router(referral_code_router)
