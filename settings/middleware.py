from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


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