from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from db.database import Session, engine
from fastapi.responses import JSONResponse
from .schema.auth_schema import LoginModel, SignUpModel
from model.models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
session = Session(bind=engine)


@auth_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
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
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the email already exists",
                            headers=None
                            )
    db_username = session.query(User).filter(
        User.username == user.username).first()
    if db_username is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists",
                            headers=None
                            )
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=True if (db_email or db_username) is None else False,
        is_staff=user.is_staff
    )
    session.add(new_user)
    session.commit()
    response.status_code = status.HTTP_201_CREATED
    return new_user


# login route
@auth_router.post('/login')
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(
        User.username == user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
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
            "access": access_token
        }
    )
