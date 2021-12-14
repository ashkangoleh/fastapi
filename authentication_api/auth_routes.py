from fastapi import (
    APIRouter,
    status,
    Depends,
    Body,
    Request,
    UploadFile,
    File,
    Security,
    BackgroundTasks,
    Query
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from utils import CBV, GeoIpLocation
from utils.mail_service.mail_service import EmailSchema, send_email_async
from .schema.auth_schema import (
    LoginModel,
    SignUpModel,
    ResetPassword,
    UserProfileSchema,
    Settings,
    GetCodeSchema,
)
from model.models import (
    User,
    UserLog,
    CodeVerification as CVN,
    UserProfile
)
from fastapi.exceptions import HTTPException
import datetime
from fastapi_jwt_auth import AuthJWT
from utils import AuthHandler
import secrets
from PIL import Image
import os
import random
from typing import Dict, Any
from db import get_db, get_session, redis_client
from settings import limiter
from fastapi_limiter.depends import RateLimiter as RL

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)
wrapper_auth = CBV(auth_router)


async def get_current_user(token: str = Depends(AuthHandler.Token_requirement)):
    """

    Args:
        token:

    Returns:

    """
    username = token.get_jwt_subject()
    user = token.get_raw_jwt()[username]
    return user


@auth_router.get('/')
async def hello(Authorize: str = Depends(AuthHandler.Token_requirement)):
    """normal route for check authentication

    Args:
        Authorize (AuthJWT, optional): User based on jwt. Defaults to Depends().

    Raises:
        HTTPException: 401 Unauthorized user

    Returns:
        str: message
    """
    return {
        "message": "This is Authentication route"
    }


# signup route
@auth_router.post('/signup', response_model=SignUpModel)
async def signUp(user: SignUpModel, response: Response, db: get_session = Depends(get_db)):
    """user registration

    Args:
        db: get_session which depends on get_db function
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
    db_email = db.query(User).filter(User.email == user.email).first()
    db_username = db.query(User).filter(
        User.username == user.username).first()
    db_phone_number = db.query(User).filter(
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
        "is_active": True if user.phone_number is not None else False,
        "is_staff": False
    }
    new_user = User(**user_dict)
    user.password2 = user.hashed_password()
    db.add(new_user)
    db.commit()
    resp = {
        "status": "success",
        "message": "User created successfully",
    }
    return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)


# login route
# @auth_router.post('/login',dependencies=[Depends(RL(times=2, seconds=5))]) # ratelimiter from fastapi-limiter
@auth_router.post('/login')
# @limiter.limit("2/minute")
async def login(request: Request, user: LoginModel, Authorize: AuthJWT = Depends(),
                # query with async
                # db: Asyncget_session = Depends(get_db) 
                # none async query
                db: get_session = Depends(get_db)
                ):
    """user login

    Args:
        db: get_session which depends on get_db function
        request:
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
    # normal query
    db_user = db.query(User).filter(User.username == user.username).first()
    # async query
    # db_user = (await db.execute(select(User).where(
    #     User.username == user.username))).scalars().first()
    if db_user and AuthHandler.verify_password(db_user.password, user.password):
        user_claims = {
            db_user.username: {
                "id": db_user.id,
                "email": db_user.email,
                "phone_number": db_user.phone_number,
                "is_active": db_user.is_active,
                "is_staff": db_user.is_staff,
            }
        }
        access_token = Authorize.create_access_token(
            subject=user.username, user_claims=user_claims, algorithm='HS256')
        refresh_token = Authorize.create_refresh_token(
            subject=user.username, user_claims=user_claims, algorithm='HS256')
        ip_loc = request.client.host
        geo = await GeoIpLocation(ip_loc)
        if geo['status'] != "fail":
            # none async query
            geoLoc = UserLog(user_id=db_user.id, user_log=geo)
            db.add(geoLoc)
            db.commit()
            # async query
            # geoLoc = UserLog(user_id=db_user.id, user_log={"query": ip_loc})
            # db.add(geoLoc)
            # await db.commit()
        else:
            # none async query
            geoLoc = UserLog(user_id=db_user.id, user_log=geo)
            db.add(geoLoc)
            db.commit()
            # async query
            # geoLoc = UserLog(user_id=db_user.id, user_log={"query": ip_loc})
            # db.add(geoLoc)
            # await db.commit()
        resp = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return JSONResponse(content=resp, status_code=status.HTTP_201_CREATED)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password")


# refresh token route
@auth_router.get('/refresh')
async def refresh_token(Authorize: str = Depends(AuthHandler.Refresh_token_requirement),
                        db: get_session = Depends(get_db)):
    """refresh token

    Args:
        db: get_session which depends on get_db function
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
    current_user = Authorize.get_jwt_subject()
    db_user = db.query(User).filter(User.username == current_user).first()
    if db_user.is_active:
        user_claims = {
            db_user.username: {
                "id": db_user.id,
                "email": db_user.email,
                "phone_number": db_user.phone_number,
                "is_active": db_user.is_active,
                "is_staff": db_user.is_staff,
            }
        }
        access_token = Authorize.create_access_token(
            subject=current_user, user_claims=user_claims, algorithm='HS256')

        return jsonable_encoder(
            {
                "access_token": access_token
            }
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User is not active")


# revoke access and refresh token
@auth_router.delete('/access-revoke')
def access_revoke(Authorize: str = Depends(AuthHandler.Token_requirement)):
    Authorize.jwt_required()

    jti = Authorize.get_raw_jwt()['jti']
    redis_client.setex(jti, Settings().access_expires, 'true')
    return {"detail": "Access token has been revoke"}


@auth_router.delete('/refresh-revoke')
def refresh_revoke(Authorize: str = Depends(AuthHandler.Refresh_token_requirement)):
    Authorize.jwt_refresh_token_required()

    jti = Authorize.get_raw_jwt()['jti']
    redis_client.setex(jti, Settings().refresh_expires, 'true')
    return {"detail": "Refresh token has been revoke"}


# user change and reset password
@wrapper_auth('/password', dependencies=[Depends(RL(times=2, minutes=3))])
# @limiter.limit("5/minute")   # not working on websocket yet
class ResetPassword:
    async def get(query: GetCodeSchema = Depends(), db: get_session = Depends(get_db)):
        CVN.old_code_remover(db)
        db_user = db.query(User).filter(
            User.username == query.username).first()
        if db_user:
            if db_user.is_active:
                random_code = random.randint(1000, 9999)
                if query.plan == 'email':
                    code = CVN(user_id=db_user.id, code=str(random_code))
                    db.add(code)
                    db.commit()
                    response = {
                        "status": "success",
                        "message": "verify code already send"
                    }
                    await send_email_async(
                        subject="Verify Code",
                        email_to=[db_user.email],
                        body={
                            "title": f"{db_user.username}",
                            "name": f"verify code is: {random_code}"
                        }
                    )
                    return JSONResponse(status_code=200, content={"message": "email has been sent"})
                elif query.plan == 'mobile':
                    code = CVN(user_id=db_user.id, code=str(random_code))
                    db.add(code)
                    db.commit()
                    return JSONResponse(status_code=200, content={"message": "sms has been sent"})
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="query params not valid")
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="User is not active")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    def post(request: ResetPassword, db: get_session = Depends(get_db)):
        db_user = db.query(User).filter(
            User.username == request.username).first()
        verify_code = db.query(CVN).filter(
            User.username == request.username).order_by(CVN.id.desc()).first()
        if db_user:
            if db_user.is_active:
                if db_user.id == verify_code.user_id:
                    if verify_code.validation and verify_code.expiration_time < (
                            datetime.datetime.now() + datetime.timedelta(minutes=2)):
                        if verify_code.code == request.code:
                            db_user.password = request.hashed_password()
                            verify_code.validation = False
                            db.commit()
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
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="User is not active")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )

    def patch(request: Dict = Body(...), db: get_session = Depends(get_db)):
        db_user = db.query(User).filter(
            User.username == request['username']).first()
        if db_user:
            if db_user.is_active:
                if AuthHandler.verify_password(db_user.password, request['password']):
                    new_password = AuthHandler.get_password_hash(
                        request['new_password'])
                    if not AuthHandler.verify_password(db_user.password, request['new_password']):
                        db_user.password = new_password
                        db.commit()
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
                        "message": "username / password is not correct"
                    }
                    return JSONResponse(content=response, status_code=status.HTTP_400_BAD_REQUEST)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="User is not active")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )


# user log
@auth_router.get("/userlog")
async def user_log(db: get_session = Depends(get_db), current_user: User = Security(get_current_user)):
    db_log = db.query(UserLog).filter(UserLog.user_id ==
                                      current_user['id']).order_by(UserLog.id.desc()).all()[:10]
    data = {logs.login_datetime.timestamp(): logs.user_log for logs in db_log}
    return jsonable_encoder(data)


# user profile
@wrapper_auth('/profile')
class Profile:
    # def post(profile: UserProfileSchema, _user=Depends(AuthHandler.Token_requirement)):
    #             with form data
    async def post(profile: UserProfileSchema = Depends(UserProfileSchema.as_form), file: UploadFile = File(...),
                   current_user: User = Security(get_current_user), db: get_session = Depends(get_db)):
        db_user = db.query(User).filter(
            User.id == current_user['id']).first()
        db_profile = db.query(UserProfile).filter(
            UserProfile.user_id == db_user.id).first()
        if not db_profile:
            file_content = await file.read()
            generated_name = ""
            FILEPATH = "media/profile_image/"
            extension = file.filename.split(".")[1]
            token_name = secrets.token_hex(10) + "." + extension
            if not os.path.exists(FILEPATH + f'{db_user.id}'):
                make_user_dir: Any = os.mkdir(FILEPATH + f'{db_user.id}')
                generated_name += make_user_dir + "/" + token_name
            else:
                generated_name += FILEPATH + f'{db_user.id}/' + token_name
            if extension not in ["jpg", "png"]:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="file extension is not valid"
                )
            if not os.path.exists(generated_name):
                with open(generated_name, "wb") as file_object:
                    file_object.write(file_content)
                img = Image.open(generated_name)
                img = img.resize(size=(200, 200))
                img.save(generated_name)
                file_object.close()
                try:
                    url = str(generated_name)
                    profile.image = url
                    user_profile = UserProfile(
                        user_id=db_user.id,
                        first_name=profile.first_name,
                        last_name=profile.last_name,
                        address=profile.address,
                        image=profile.image,
                        postal_code=profile.postal_code,
                        national_code=profile.national_code,
                    )
                    db.add(user_profile)
                    db.commit()
                    response = {
                        "user": db_user.username,
                        "first_name": profile.first_name,
                        "last_name": profile.last_name,
                        "address": profile.address,
                        "image": profile.image
                    }
                    return jsonable_encoder(response)
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User profile already exists"
                    )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="file already exists"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="User profile already exists"
            )

    def get(current_user: User = Security(get_current_user), db: get_session = Depends(get_db)):
        # user_id = _user.get_raw_jwt()['user']['id']
        print(current_user.get("id"))
        db_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user['id']).first()
        if db_profile:
            return jsonable_encoder(
                {
                    "Username": db_profile.user.username,
                    "first_name": db_profile.first_name,
                    "last_name": db_profile.last_name,
                    "address": db_profile.address,
                    "image": db_profile.image
                }
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="user does not exists",
            )

    def patch(profile: UserProfileSchema, _user=Depends(AuthHandler.Token_requirement),
              db: get_session = Depends(get_db)):
        user_id = _user.get_raw_jwt()['user']['id']
        db_profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id).first()
        if db_profile:
            db_profile.first_name = profile.first_name
            db_profile.last_name = profile.last_name
            db_profile.address = profile.address
            db.commit()
            return jsonable_encoder({
                "status": "success",
                "message": f"{db_profile.user.username}'s profile updated"
            })


# mail service
# send mail with async
@auth_router.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:
    await send_email_async(
        subject=email.dict().get("subject"),
        email_to=email.dict().get("email"),
        body=email.dict().get("body")
    )
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


# send mail with backgroundTasks


@auth_router.post("/emailbackground")
async def send_in_background(
        background_tasks: BackgroundTasks,
        email: EmailSchema
) -> JSONResponse:
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
