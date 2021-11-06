from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.functions import current_user, user
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
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
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
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{user.username} is not superuser"
    )

# user order


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
        order = user.orders
        if not len(order):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order Not Found"
            )
        else:
            return jsonable_encoder(order)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"{user.username} is not active"
    )

#  get current user specific order


@order_router.get('/user/order/{id}')
async def get_user_specific_order(id: int, Authorize: AuthJWT = Depends()):
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
        orders = user.orders

        for obj in orders:
            if obj.id == id:
                return jsonable_encoder(obj)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No order Found"
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{user.username} is not active"
    )
# update order


@order_router.patch('/update/{id}')
async def update_order(id: int, order: order_schema.OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_active or user.is_staff:
        order_update = session.query(Order).filter(Order.id == id).first()
        if order_update.order_status == "PENDING":
            order_update.quantity = order.quantity
            order_update.order_sizes = order.order_sizes
            session.commit()
            response = {
                "id": order_update.id,
                "quantity": order_update.quantity,
                "order_sizes": order_update.order_sizes,
                "order_status": order_update.order_status,
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(
                status_code=status.HTTP_226_IM_USED,
                detail="Your Order/s already in action"
            )


# order status route
@order_router.patch('/admin/update/{id}')
async def update_order_status(id: int, order: order_schema.OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        update_order_status = session.query(
            Order).filter(Order.id == id).first()
        update_order_status.order_status = order.order_status
        session.commit()
        # order_updated = session.query(Order).filter(Order.id == id).first()
        response = {
            "id": update_order_status.id,
            "quantity": update_order_status.quantity,
            "order_sizes": update_order_status.order_sizes,
            "order_status": update_order_status.order_status,
        }
        return jsonable_encoder(response)


# delete order
@order_router.delete('/admin/delete/{id}')
async def delete_order(id: int, Authorize: AuthJWT = Depends()):
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
        order_to_delete = session.query(Order).filter(Order.id == id).first()
        if order_to_delete:
            session.delete(order_to_delete)
            session.commit()
            return order_to_delete
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
