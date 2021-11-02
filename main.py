import uvicorn
from fastapi import FastAPI
from sqlalchemy import log
from authentication_api.auth_routes import auth_router
from authentication_api.schema.auth_schema import SignUpModel
from order_api.order_routes import order_router
from authentication_api.schema import auth_schema
from fastapi_jwt_auth import AuthJWT


app = FastAPI(
    title="core_api",

)

@AuthJWT.load_config
def get_config():
    return auth_schema.Settings()



app.include_router(
    auth_router,
    prefix="/api/v1",
    # responses={
    #     400: {"description": "already exists"},
    #     201: {"model": SignUpModel}
    # }
)
app.include_router(
    order_router,
    prefix="/api/v1"
)


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=True)