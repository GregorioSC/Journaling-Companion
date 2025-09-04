from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security.tokens import decode_token
from services.user_service import UserService
from dao.user_dao import UserDAO

bearer = HTTPBearer()


def get_user_service():
    return UserService(UserDAO())


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    user_svc: UserService = Depends(get_user_service),
):
    try:
        claims = decode_token(creds.credentials)
        user_id = int(claims["sub"])
        user = user_svc.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
