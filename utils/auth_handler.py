from fastapi_jwt_auth import AuthJWT
from fastapi import status, Depends
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash


class AuthHandler:

    @staticmethod
    def verify_password(hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)

    @staticmethod
    def get_password_hash(password):
        return generate_password_hash(password)

    @staticmethod
    def Token_requirement(Authorize: AuthJWT = Depends()):
        try:
            Authorize.jwt_required()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
        return Authorize

    @staticmethod
    def Refresh_token_requirement(Authorize: AuthJWT = Depends()):
        try:
            Authorize.jwt_refresh_token_required()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Refresh Token"
            )
        return Authorize
