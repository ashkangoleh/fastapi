from core.authentication_api.auth_routes import auth_router
from core.order_api.order_routes import order_router
from db.schema import auth_schema
from core.overview.index import app_view
from fastapi_jwt_auth import AuthJWT
from core.uploader import upload_file
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
        prefix="/ws/v1"
    )
    app.include_router(
        upload_file.file_router,
    )
    app.include_router(
        app_view,
    )