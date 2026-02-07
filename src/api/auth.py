# src/api/auth.py
from fastapi import APIRouter, HTTPException, Response, Depends, status
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from authx import AuthX
from datetime import timedelta

from src.config import get_authx_config, settings
from src.dependencies import get_db

from src.schemas.auth import TokenResponse, UserResponse, UserSchema, UserRegisterSchema
from src.service.auth import Auth


router = APIRouter(prefix="/auth", tags=["Аутентификация"])
security = AuthX(config=get_authx_config())
http_bearer = HTTPBearer()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Аутентификация пользователя и получение JWT токена"
)
async def login(
        credentials: UserSchema,
        response: Response,
        conn=Depends(get_db)
):
    auth = Auth(conn)

    user = await auth.get_user_by_field("username", credentials.username)
    if not user:
        raise HTTPException(...)

    # добавить хэширование пароля
    if credentials.password != user['password']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    # Создаем токен
    token = security.create_access_token(
        uid=str(user['id']),
        data={
            'username': user['username'],
            'email': user['email'],
            'role': user.get('role', 'user')
        },
        expires_delta=timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    )

    # Устанавливаем токен в cookie
    response.set_cookie(
        key=security._config.JWT_ACCESS_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite='lax',
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRES,
        secure=not settings.DEBUG  # Только HTTPS в production
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRES
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register(
        user_data: UserRegisterSchema,
        conn=Depends(get_db)
):
    auth = Auth(conn)

    existing_user = await auth.get_user_by_field("username", user_data.username)
    existing_email = await auth.get_user_by_field("email", user_data.email)

    if existing_user or existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже существует"
        )

    user = await auth.create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        phone_number=user_data.phone
    )

    return UserResponse(
        id=user['id'],
        username=user['username'],
        email=user['email'],
    )
