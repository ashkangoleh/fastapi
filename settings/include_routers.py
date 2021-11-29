from authentication_api.auth_routes import auth_router
from order_api.order_routes import order_router
from authentication_api.schema import auth_schema
from fastapi_jwt_auth import AuthJWT
from uploader import upload_file
from ws.ws import ws

@AuthJWT.load_config
def get_config():
    return auth_schema.Settings()


def include_router(app):
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
    app.include_router(
        upload_file.file_router,
    )