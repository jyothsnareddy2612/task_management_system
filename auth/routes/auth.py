from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from auth.dependencies import get_auth_service, get_current_user
from auth.settings import get_auth_settings
from src.config.settings import Settings
from src.core.services.auth_service import AuthService
from src.data.models.postgres.user import User
from src.schemas.auth import (
    GoogleCallbackResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPair,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> User:
    return await service.register(payload)


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenPair:
    return await service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    return await service.refresh(payload.refresh_token)


@router.get("/google/login", status_code=307)
async def google_login(service: AuthService = Depends(get_auth_service)) -> RedirectResponse:
    return RedirectResponse(service.build_google_authorization_url())


@router.get("/google/callback", response_model=GoogleCallbackResponse)
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_auth_settings),
) -> GoogleCallbackResponse | RedirectResponse:
    user, tokens = await service.login_with_google(code, state)
    if settings.oauth_success_redirect_url:
        redirect_url = (
            f"{settings.oauth_success_redirect_url}"
            f"?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
        )
        return RedirectResponse(redirect_url)
    return GoogleCallbackResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
