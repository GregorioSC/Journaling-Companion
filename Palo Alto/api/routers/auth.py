from fastapi import APIRouter, Depends, HTTPException
from api.schemas.auth import LoginRequest, TokenResponse
from api.schemas.user import UserCreate, UserOut
from services.auth_service import AuthService
from services.user_service import UserService
from dao.user_dao import UserDAO
from models.user import User

router = APIRouter()


def get_auth_service():
    return AuthService(UserDAO())


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, svc: AuthService = Depends(get_auth_service)):
    u = User(
        id=None,
        username=payload.username,
        email=payload.email,
        password=payload.password,  # hashed inside AuthService.register
        age=payload.age,
        gender=payload.gender,
    )
    saved = svc.register(u)
    return UserOut(
        id=saved.id,
        username=saved.username,
        email=saved.email,
        age=saved.age,
        gender=saved.gender,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, svc: AuthService = Depends(get_auth_service)):
    token = svc.login(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return TokenResponse(access_token=token)
