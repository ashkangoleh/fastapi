import random
from typing import Dict
from fastapi import APIRouter, status, Depends, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from starlette.requests import Request
from db.database import session
from utils import CBV, GeoIpLocation
from .schema.auth_schema import (
    LoginModel,
    SignUpModel,
    verify_password,
    ResetPassword,
    get_password_hash,
    verify_password
)
from model.models import (
    User,
    UserLog,
    CodeVerification as CVN
)
from fastapi.exceptions import HTTPException
import datetime
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)
wrapper_auth = CBV(auth_router)


@auth_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    """normal route for check authentication

    Args:
        Authorize (AuthJWT, optional): User based on jwt. Defaults to Depends().

    Raises:
        HTTPException: 401 Unauthorized user

    Returns:
        str: message
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    return {
        "message": "This is Authentication route"
    }

# signup route


@auth_router.post('/signup', response_model=SignUpModel)
async def signUp(user: SignUpModel, response: Response):
    """user registration

    Args:
        user (SignUpModel): signup Schema
        response (Response): custom response

    Raises:
        HTTPException: existing email on 1st raise
        HTTPException: existing username on 2nd raise
    Requests:
        dict:
        {
            "username": string,
            "email": string(email),
            "password": string
        }
    Returns:
        dict:
        {
            "id": int,
            "username": string,
            "email": string(email field),
            "password": string(hashed password),
            "is_staff": boolean,
            "is_active": boolean
        }
    """
    db_email = session.query(User).filter(User.email == user.email).first()
    db_username = session.query(User).filter(
        User.username == user.username).first()
    db_phone_number = session.query(User).filter(
        User.phone_number == user.phone_number).first()
    if db_email is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the email already exists",
                            headers=None
                            )
    if db_username is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists",
                            headers=None
                            )
    if db_phone_number is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="phone number already exists",
                            headers=None
                            )
    user_dict = {
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "password": user.hashed_password(),
        "is_active": True if (db_phone_number) is None else False,
        "is_staff": user.is_staff
    }
    new_user = User(**user_dict)
    user.password2 = user.hashed_password()
    session.add(new_user)
    session.commit()
    resp = {
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "password": user.hashed_password(),
        "password2": user.password2,
    }
    return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)


# login route
@auth_router.post('/login')
async def login(request: Request, user: LoginModel, Authorize: AuthJWT = Depends()):
    """user login

    Args:
        user (LoginModel): Login Schema
        Authorize (AuthJWT, optional): User based on jwt. Defaults to Depends().

    Raises:
        HTTPException: username and password validation error

    Requests:
        dict:
        {
            "username":string,
            "password":string
        }
    Returns:
        dict:
        {
            "access_token":string(jwt.access_token),
            "refresh_token":string(jwt.refresh_token)
        }

    """
    db_user = session.query(User).filter(
        User.username == user.username).first()
    if db_user and verify_password(db_user.password, user.password):
        user_claims = {
            "detail": {
                "phone_number": db_user.phone_number,
                "is_active": db_user.is_active,
                "is_staff": db_user.is_staff,
            }
        }
        access_token = Authorize.create_access_token(subject=user.username, user_claims=user_claims,algorithm='HS512')
        refresh_token = Authorize.create_refresh_token(subject=user.username,user_claims=user_claims,algorithm='HS512')
        ip_loc = request.client.host
        geo = GeoIpLocation(ip_loc)
        geoLoc = UserLog(user_id=db_user.id, user_log=geo)
        session.add(geoLoc)
        session.commit()
        resp = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password")


# refresh token route

@auth_router.get('/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):
    """refresh token

    Args:
        Authorize (AuthJWT, optional): User based on jwt. Defaults to Depends().

    Raises:
        HTTPException: refresh token validation error

    Request:
        bearer jwt refresh token

    Returns:
        dict: 
        {
            "access_token":string(jwt.access_token)
        }
    """
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Refresh Token"
        )
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()
    user_claims = {
                "detail": {
                    "phone_number": db_user.phone_number,
                    "is_active": db_user.is_active,
                    "is_staff": db_user.is_staff,
                }
            }
    access_token = Authorize.create_access_token(subject=current_user,user_claims=user_claims,algorithm='HS512')

    return jsonable_encoder(
        {
            "access_token": access_token
        }
    )


@wrapper_auth('/password')
class ResetPassword():

    def get(request: Dict = Body(...)):
        db_user = session.query(User).filter(
            User.username == request['username']).first()
        if db_user:
            random_code = random.randint(1000, 9999)
            code = CVN(user_id=db_user.id, code=str(random_code))
            session.add(code)
            session.commit()
            response = {
                "status": "success",
                "message": "verify code already send"
            }
            return JSONResponse(content=response, status_code=status.HTTP_200_OK)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    def post(request: ResetPassword):
        db_user = session.query(User).filter(
            User.username == request.username).first()
        verify_code = session.query(CVN).filter(
            User.username == request.username).order_by(CVN.id.desc()).first()
        if db_user:
            if db_user.id == verify_code.user_id:
                if verify_code.validation == True and verify_code.expiration_time < (datetime.datetime.now() + datetime.timedelta(minutes=2)):
                    if verify_code.code == request.code:
                        db_user.password = request.hashed_password()
                        verify_code.validation = False
                        session.commit()
                        resp = {
                            "status": "success",
                            "message": "Password changed successfully"
                        }
                        return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="verification code is not valid"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="verification code expired"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="invalid username"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )

    def patch(response: Response, request: Dict = Body(...)):
        db_user = session.query(User).filter(
            User.username == request['username']).first()
        if db_user:
            if verify_password(db_user.password, request['password']):
                new_password = get_password_hash(request['new_password'])
                if not verify_password(db_user.password, request['new_password']):
                    db_user.password = new_password
                    session.commit()
                    response = {
                        "status": "success",
                        "message": f"{db_user.username} password changed"
                    }
                    return JSONResponse(content=response, status_code=status.HTTP_201_CREATED)
                else:
                    response = {
                        "status": "fail",
                        "message": "new password is same as old password choose another password"
                    }
                    return JSONResponse(content=response, status_code=status.HTTP_400_BAD_REQUEST)
            else:
                response = {
                    "status": "fail",
                    "message": "username / password is not currect"
                }
                return JSONResponse(content=response, status_code=status.HTTP_400_BAD_REQUEST)


@auth_router.get("/userlog")
async def user_log(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    current_user = Authorize.get_jwt_subject()
    db_log = session.query(UserLog).filter(User.username == current_user).all()
    data = {logs.login_datetime.timestamp(): logs.user_log for logs in db_log}
    return jsonable_encoder(data)
