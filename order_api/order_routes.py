from fastapi import APIRouter


order_router = APIRouter(
    prefix= '/order',
    tags=['orders']
)

@order_router.get('/')
async def hello():
    return {
        "message":"This is Order route"
    }