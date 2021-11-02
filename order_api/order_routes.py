from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from .schema import order_schema
from model.models import User, Order
from fastapi_jwt_auth import AuthJWT
from db.database import session
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

order_router = APIRouter(
    prefix='/order',
    tags=['orders']
)


@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return {
        "message": "This is Order route"
    }


@order_router.post('/order')
async def place_an_order(order: order_schema.OrderModel, response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        order_sizes=order.order_sizes,
        quantity=order.quantity,
    )

    new_order.user = user

    session.add(new_order)
    session.commit()
    response.status_code = status.HTTP_201_CREATED
    resp = {
        "order_size": new_order.order_sizes,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }
    return jsonable_encoder(resp)


# list of orders

@order_router.get('/order_list')
async def list_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        orders = session.query(Order).all()
        return jsonable_encoder(orders)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be superUser"
    )
# get single order


@order_router.get('/orders/{id}')
async def get_order_by_id(id:int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    user = Authorize.get_jwt_subject()
    
    current_user = session.query(User).filter(User.username == user).first()
    
    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order Not Found"
    )


@order_router.get('/user/orders')
async def list_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username == current_user).first()
    
    if user.is_active:
        return jsonable_encoder(user.orders)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be superUser"
    )
