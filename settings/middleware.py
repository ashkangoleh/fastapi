from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from decouple import config
import aioredis

limiter = Limiter(key_func=get_remote_address)
class Middleware:
    REDIS_LIMITER = config('REDIS_LIMITER')
    ORIGINS = [
        "http://localhost",
        "http://localhost:8080",
    ]
    ALLOWED_HOSTS = [
        "*",
    ]

    def __init__(self, app) -> None:
        self.app = app

    def allowed_domains(self):
        self.app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=self.ALLOWED_HOSTS,
        )

    def cors_origins(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def staticFiles(self):
        self.app.mount("/media", StaticFiles(directory="media"), name="media")
        self.app.mount(
            "/static", StaticFiles(directory="static"), name="static")

    def rate_limit(self):
        self.app.state.limiter = limiter
        self.app.add_exception_handler(
            RateLimitExceeded, _rate_limit_exceeded_handler)
        
    async def limiter_conf(self):
        rate_limiter = await aioredis.from_url(f"{self.REDIS_LIMITER}", encoding="utf-8", decode_responses=True, db=2)
        await FastAPILimiter.init(prefix="core_api",redis=rate_limiter)