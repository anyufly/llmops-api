import base64
import uuid
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Callable

from loguru._logger import Logger
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from llmops_api.base.config.config import AuthConfig
from llmops_api.exception.auth import (
    AccessTokenExpire,
    AccessTokenNotExpire,
    OldPasswordWrong,
    RefreshTokenExpire,
    UsernameOrPasswordWrong,
)
from llmops_api.repo.user import UserRepo
from llmops_api.view.auth import TokensViewModel
from llmops_api.view.user import UserViewModel


@dataclass
class TokensInfo:
    access_token: str
    refresh_token: str
    user_id: int


class AuthService:
    def __init__(
        self,
        repo: UserRepo,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        redis_client_factory: Callable[..., AbstractAsyncContextManager[Redis]],
        auth_config: AuthConfig,
        logger: Logger,
    ):
        self.repo = repo
        self.transaction_factory = transaction_factory
        self.redis_client_factory = redis_client_factory
        self.auth_config = auth_config
        self.logger = logger

    async def login(self, username: str, password: str) -> TokensViewModel:
        async with self.transaction_factory() as session:
            user = await self.repo.get_by_username(session, username)

            if user is None:
                raise UsernameOrPasswordWrong

            if user.check_password(password):
                tokens = self._generate_tokens(user.id)
                return await self._save_tokens(tokens)
            else:
                raise UsernameOrPasswordWrong

    async def change_pass(self, user_id: int, old_pass: str, new_pass: str):
        async with self.transaction_factory() as session:
            user = await self.repo.get_by_id(session, user_id)
            if not user.check_password(old_pass):
                raise OldPasswordWrong

            user.set_password(new_pass)
            user.update_by = user_id
            await self.repo.add(session, user)

    async def fetch_user_id(self, access_token: str) -> UserViewModel:
        async with self.redis_client_factory() as client:
            user_id = await client.get(self._get_access_token_key(access_token))

            if user_id is None:
                raise AccessTokenExpire

            return int(user_id.decode("utf-8"))

    async def refresh_token(self, access_token: str, refresh_token: str):
        return await self._refresh_tokens(access_token, refresh_token)

    async def logout(self, access_token: str, refresh_token: str) -> None:
        await self._delete_tokens(access_token, refresh_token)

    @staticmethod
    def _generate_tokens(user_id: int) -> TokensInfo:
        access_token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")
        refresh_token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")

        return TokensInfo(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    def _get_access_token_key(access_token: str) -> str:
        return f"accessToken:{access_token}"

    @staticmethod
    def _get_refresh_token_key(access_token: str, refresh_token: str) -> str:
        return f"refreshToken:{access_token}:{refresh_token}"

    async def _save_tokens(self, info: TokensInfo) -> TokensViewModel:
        async with self.redis_client_factory() as client:
            access_token_key = self._get_access_token_key(info.access_token)
            refresh_token_key = self._get_refresh_token_key(info.access_token, info.refresh_token)
            await client.set(
                access_token_key,
                str(info.user_id),
                ex=self.auth_config.access_token_expire,
            )
            await client.set(
                refresh_token_key,
                str(info.user_id),
                ex=self.auth_config.refresh_token_expire,
            )

            return TokensViewModel(access_token=info.access_token, refresh_token=info.refresh_token)

    async def _refresh_tokens(self, access_token: str, refresh_token: str) -> TokensViewModel:
        async with self.redis_client_factory() as client:
            access_token_exists = await client.exists(self._get_access_token_key(access_token))

            if access_token_exists:
                raise AccessTokenNotExpire

            refresh_token_key = self._get_refresh_token_key(access_token, refresh_token)

            refresh_token_payload = await client.get(refresh_token_key)

            if refresh_token_payload is None:
                raise RefreshTokenExpire

            await client.delete(refresh_token_key)
            tokens = TokensInfo(
                access_token=base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8"),
                refresh_token=refresh_token,
                user_id=int(refresh_token_payload.decode("utf-8")),
            )

            return await self._save_tokens(tokens)

    async def _delete_tokens(self, access_token: str, refresh_token: str) -> None:
        async with self.redis_client_factory() as client:
            await client.delete(
                self._get_access_token_key(access_token),
                self._get_refresh_token_key(access_token, refresh_token),
            )
