from datetime import timedelta
from uuid import UUID

import httpx
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.core.exceptions import AuthenticationError, ConflictError
from src.data.models.postgres.user import User
from src.data.repositories.user_repository import UserRepository
from src.constants.enums import UserRole
from src.schemas.auth import RegisterRequest, TokenPair
from src.utils.security import create_token, decode_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)

    async def register(self, payload: RegisterRequest) -> User:
        if await self.users.get_by_email(payload.email):
            raise ConflictError("Email is already registered")
        user = User(
            name=payload.name,
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        await self.users.create(user)
        await self.session.commit()
        return user

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("User is inactive")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token, "refresh", self.settings)
        user = await self.users.get_by_id(UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid refresh token")
        return self._issue_tokens(user)

    def build_google_authorization_url(self) -> str:
        if not self.settings.google_oauth_client_id:
            raise AuthenticationError("Google OAuth is not configured")
        state = self._state_serializer().dumps({"provider": "google"})
        params = httpx.QueryParams(
            {
                "client_id": self.settings.google_oauth_client_id,
                "redirect_uri": self.settings.google_oauth_redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "access_type": "offline",
                "prompt": "consent",
                "state": state,
            }
        )
        return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"

    async def login_with_google(self, code: str, state: str) -> tuple[User, TokenPair]:
        self._validate_oauth_state(state)
        if not self.settings.google_oauth_client_id or not self.settings.google_oauth_client_secret:
            raise AuthenticationError("Google OAuth is not configured")

        async with httpx.AsyncClient(timeout=5.0) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.settings.google_oauth_client_id,
                    "client_secret": self.settings.google_oauth_client_secret.get_secret_value(),
                    "redirect_uri": self.settings.google_oauth_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code >= 400:
                raise AuthenticationError("Google token exchange failed")
            access_token = token_response.json()["access_token"]

            profile_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_response.status_code >= 400:
                raise AuthenticationError("Google profile lookup failed")

        profile = profile_response.json()
        if not profile.get("email_verified"):
            raise AuthenticationError("Google email is not verified")

        email = str(profile["email"]).lower()
        desired_role = self._role_for_google_email(email)
        user = await self.users.get_by_email(email)
        if user is None:
            user = User(
                name=str(profile.get("name") or email.split("@")[0]),
                email=email,
                hashed_password=hash_password(UUID(int=0).hex),
                role=desired_role,
            )
            await self.users.create(user)
            await self.session.commit()
        elif desired_role == UserRole.ADMIN and user.role != UserRole.ADMIN:
            user.role = UserRole.ADMIN
            await self.session.commit()
        if not user.is_active:
            raise AuthenticationError("User is inactive")
        return user, self._issue_tokens(user)

    def _role_for_google_email(self, email: str) -> UserRole:
        admin_emails = {admin_email.lower() for admin_email in self.settings.google_admin_emails}
        return UserRole.ADMIN if email.lower() in admin_emails else UserRole.WORKER

    def _state_serializer(self) -> URLSafeSerializer:
        return URLSafeSerializer(
            self.settings.jwt_secret_key.get_secret_value(),
            salt="google-oauth-state",
        )

    def _validate_oauth_state(self, state: str) -> None:
        try:
            data = self._state_serializer().loads(state)
        except BadSignature as exc:
            raise AuthenticationError("Invalid OAuth state") from exc
        if data.get("provider") != "google":
            raise AuthenticationError("Invalid OAuth provider")

    def _issue_tokens(self, user: User) -> TokenPair:
        #acess token:short lived
        #refresh token"long lived
        access = create_token(
            subject=user.id,
            role=str(user.role),
            token_type="access",
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
            settings=self.settings,
        )
        refresh = create_token(
            subject=user.id,
            role=str(user.role),
            token_type="refresh",
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
            settings=self.settings,
        )
        return TokenPair(access_token=access, refresh_token=refresh)
