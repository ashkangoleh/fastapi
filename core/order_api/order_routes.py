from typing import Any
from fastapi import APIRouter, status, Depends, Security
from fastapi import Body
from fastapi.encoders import jsonable_encoder
from db import (
    AuthHandler,
    Order,
    User,
    get_db,
    Session,
    OrderModel,
    OrderStatusModel,
    OrderTest,
    get_current_user,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from utils.celery.celery_worker import create_task


order_router = APIRouter(
    prefix='/order',
    dependencies=[Depends(AuthHandler.Token_requirement)],
    tags=['Orders']
)


@order_router.post('/test')
def add_order(order: OrderTest):
    create_task.delay(order.customer_name, order.order_quantity)
    return {"message": "Order Received! Thank you for your patience."}


@order_router.get('/')
async def hello():
    return {
        "message": "This is Order route"
    }


@order_router.get('/a')
async def hello1(request: Any = Body(...)):
    # use operations for digits in string from json or objects(dict)
    data = request.get('test')
    s = "".join([i for i in data])
    return {
        "message": "This is Order route",
        "data": eval(s)
    }


@order_router.post('/order')
async def place_an_order(order: OrderModel, response: Response,  current_user: User = Security(get_current_user),
                         db: Session = Depends(get_db)):
    """place an order

    Args:
        order (order_schema.OrderModel): Order Schema
        response (Response): custom Response
        Authorize (AuthJWT, optional): User based on jwt. Defaults to Depends().

    Raises:
        HTTPException: validation token error
    Requests:
        dict:
        {
            "order_sizes":string,
            "quantity":int
        }
    Returns:
        dict:
        {
            "order_size": {
                "code": string,
                "value": string
            },
            "quantity": int,
            "id": int,
            "order_status": {
                "code": string,
                "value": string
            }
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()

    if user.is_active:
        new_order = Order(
            order_sizes=order.order_sizes,
            quantity=order.quantity,
        )

        new_order.user = user

        db.add(new_order)
        db.commit()
        response.status_code = status.HTTP_201_CREATED
        resp = {
            "order_size": new_order.order_sizes,
            "quantity": new_order.quantity,
            "id": new_order.id,
            "order_status": new_order.order_status
        }
        return jsonable_encoder(resp)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active"
        )


# list of orders


@order_router.get('/order_list')
async def list_orders(current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    """list of orders

    Args:
        Authorize (AuthJWT, optional): User based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token validation error
        HTTPException: user type

    Returns:
        list:
        [
            dict:
            {
                same as place and order
            }
        ]
    """
    user = db.query(User).filter(User.id == current_user['id']).first()
    if user.is_active:
        orders = db.query(Order).all()
        return jsonable_encoder(orders)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be superUser"
    )


# get single order


@order_router.get('/orders/{id}')
async def get_order_by_id(id: int, current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    """get order by ID

    Args:
        id (int): Order ID
        Authorize (AuthJWT, optional): User based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token validation error
        HTTPException: user type
    Requests:
        params:string
    Returns:
        dict: 
        {
            same as place and order
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()

    if user.is_active:
        order = db.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{user.username} is not superuser"
    )


# user order


@order_router.get('/user/orders')
async def list_orders(current_user: User = Security(get_current_user), db: Session = Depends(get_db)):
    """user order list

    Args:
        Authorize (AuthJWT, optional): user based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token validation error
        HTTPException: order exists message
        HTTPException: user activation

    Returns:
        dict| list: {
            same as place and order
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()

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
async def get_user_specific_order(id: int, current_user: User = Security(get_current_user), db: Session = Depends(get_db)) -> jsonable_encoder:
    """get specific order by ID

    Args:
        id (int): order ID
        Authorize (AuthJWT, optional): user based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token valdation error
        HTTPException: order existing messages
        HTTPException: user activation

    Returns:
        dict: 
        {
            same as place and order
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()
    if user.is_active:
        orders = user.orders
        # if orders:
        for obj in orders:
            if obj.id == id:
                return jsonable_encoder(obj)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"order number {id} not found"
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{user.username} is not active"
    )


# update order
@order_router.patch('/{id}')
async def update_order(id: int, order: OrderModel, response: Response,
                       current_user: User = Security(get_current_user), db: Session = Depends(get_db)) -> jsonable_encoder:
    """update order

    Args:
        id (int): order ID
        order (order_schema.OrderModel): Order Schema
        Authorize (AuthJWT, optional): user based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token validation error
        HTTPException: order in Action
    Requests:
        dict:
        {
            "order_sizes":string,
            "quantity":int
        }
    Returns:
        dict: 
        {
            same as place in order
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()
    if user.is_active or user.is_staff:
        order_update = db.query(Order).filter(Order.id == id).first()
        if order_update.order_status == "PENDING":
            order_update.quantity = order.quantity
            order_update.order_sizes = order.order_sizes
            db.commit()
            resp = {
                "id": order_update.id,
                "quantity": order_update.quantity,
                "order_sizes": order_update.order_sizes,
                "order_status": order_update.order_status,
            }
            response.status_code = status.HTTP_201_CREATED
            return jsonable_encoder(resp)
        else:
            raise HTTPException(
                status_code=status.HTTP_226_IM_USED,
                detail="Your Order/s already in action"
            )


# update order status
@order_router.patch('/status/{id}')
async def update_order_status(id: int, order: OrderStatusModel, response: Response,
                              current_user: Security = Depends(get_current_user), db: Session = Depends(get_db)) -> jsonable_encoder:
    """update status order

    Args:
        id (int): order ID
        order (order_schema.OrderStatusModel): OrderStatus Schema
        Authorize (AuthJWT, optional): user based on JWT. Defaults to Depends().

    Raises:
        HTTPException: token validation error

    Requests:
        dict:
        {
            "order_status":string
        }
    Returns:
        dict: 
        {
            same as place in order
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()
    if user.is_staff:
        update_order_status = db.query(
            Order).filter(Order.id == id).first()
        if update_order_status:
            update_order_status.order_status = order.order_status
            db.commit()
            resp = {
                "id": update_order_status.id,
                "quantity": update_order_status.quantity,
                "order_sizes": update_order_status.order_sizes,
                "order_status": update_order_status.order_status,
            }
            response.status_code = status.HTTP_201_CREATED
            return jsonable_encoder(resp)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )


# delete order
@order_router.delete('/user/order/{id}')
async def delete_order(id: int, response: Response, current_user: User = Security(get_current_user),
                       db: Session = Depends(get_db)) -> jsonable_encoder:
    """delete order

    Args:
        id (int): order ID
        Authorize (AuthJWT, optional): user based on jwt. Defaults to Depends().

    Raises:
        HTTPException: token validation error
        HTTPException: order existing Message
    Requests:
        params:string
    Returns:
        dict:
        {
            "id": int,
            "detail": string
        }
    """
    user = db.query(User).filter(User.id == current_user['id']).first()
    # if user.is_staff:
    if user:
        order_to_delete = db.query(Order).filter(Order.id == id).first()
        if order_to_delete:
            db.delete(order_to_delete)
            db.commit()
            resp = {
                "id": order_to_delete.id,
                "detail": "Order has been deleted"
            }
            response.status_code = status_code = status.HTTP_201_CREATED
            return jsonable_encoder(resp)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
