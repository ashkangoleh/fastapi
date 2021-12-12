from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)

class Middleware:
    ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    ]
    ALLOWED_HOSTS = [
        "*",
    ]
    def __init__(self,app) -> None:
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
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        
    def rate_limit(self):
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)