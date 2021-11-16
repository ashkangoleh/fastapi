from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response,JSONResponse
from db.database import session
from .schema.auth_schema import LoginModel, SignUpModel, verify_password, get_password_hash
from model.models import User
from fastapi.exceptions import HTTPException

from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


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
    response.status_code = status.HTTP_201_CREATED
    return JSONResponse(content=resp)


# login route
@auth_router.post('/login')
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
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
        access_token = Authorize.create_access_token(subject=user.username)
        refresh_token = Authorize.create_refresh_token(subject=user.username)

        resp = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return jsonable_encoder(resp)
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

    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder(
        {
            "access_token": access_token
        }
    )
