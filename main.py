from fastapi.routing import APIRoute
import inspect
import re
from fastapi.openapi.utils import get_openapi
import uvicorn
from fastapi import FastAPI
from authentication_api.auth_routes import auth_router
from order_api.order_routes import order_router
from authentication_api.schema import auth_schema
from fastapi_jwt_auth import AuthJWT
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from ws.ws import ws

app = FastAPI(
    title="core_api",
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*",]
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


@AuthJWT.load_config
def get_config():
    return auth_schema.Settings()


app.include_router(
    auth_router,
    prefix="/api/v1",
)
app.include_router(
    order_router,
    prefix="/api/v1"
)
app.include_router(
    ws,
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)