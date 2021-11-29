from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from authentication_api.schema import auth_schema
from fastapi_jwt_auth import AuthJWT
from db.init_db import init_db
from settings.middleware import Middleware
from settings.include_routers import include_router
from db.database import redis_conn
import uvicorn
import re
import inspect

tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations with users.",
    },
    {
        "name": "Orders",
        "description": "Operations with orders.",
    },
    {
        "name": "Websocket",
        "description": "websocket",
        "externalDocs": {
            "description": "websocket external docs",
        },
    },
]
app = FastAPI(
    title="core_api",
    debug=True,
    openapi_tags=tags_metadata
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Core API",
        version="1.0",
        description="An API with an Authorize Button",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


middleware = Middleware(app)
middleware.cors_origins()
middleware.staticFiles()
middleware.allowed_domains()
include_router(app)


@AuthJWT.load_config
def get_config():
    return auth_schema.Settings()

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=30)
