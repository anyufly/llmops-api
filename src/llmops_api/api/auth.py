from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from loguru._logger import Logger
from typing_extensions import Annotated

from llmops_api.base.response.base_response import BaseResponse, Empty
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.auth import ChangePassForm, LoginForm, LogoutForm, RefreshTokenForm
from llmops_api.service.auth import AuthService
from llmops_api.service.user import UserService
from llmops_api.view.auth import TokensViewModel
from llmops_api.view.user import UserViewModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/change_pass", description="修改密码", response_model=BaseResponse[Empty])
@inject
async def change_pass(
    auth_service: Annotated[AuthService, Depends(Provide["auth_module.auth_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    change_pass_form: ChangePassForm,
):
    await auth_service.change_pass(
        current_user_id,
        change_pass_form.old_password,
        change_pass_form.new_password,
    )

    return BaseResponse[Empty](code=SUCCESS_CODE, data=Empty(), msg="修改用户密码成功")


@router.post("/login", description="登录", response_model=BaseResponse[TokensViewModel])
@inject
async def login(
    auth_service: Annotated[AuthService, Depends(Provide["auth_module.auth_service"])],
    login_form: LoginForm,
):
    tokens = await auth_service.login(login_form.username, login_form.password)
    return BaseResponse[TokensViewModel](code=SUCCESS_CODE, data=tokens, msg="登录成功")


@router.post(
    "/refresh_token", description="刷新token", response_model=BaseResponse[TokensViewModel]
)
@inject
async def refresh_token(
    auth_service: Annotated[AuthService, Depends(Provide["auth_module.auth_service"])],
    refresh_token_form: RefreshTokenForm,
):
    tokens = await auth_service.refresh_token(
        refresh_token_form.access_token, refresh_token_form.refresh_token
    )
    return BaseResponse[TokensViewModel](code=SUCCESS_CODE, data=tokens, msg="刷新token成功")


@router.post("/logout", description="注销", response_model=BaseResponse[Empty])
@inject
async def logout(
    auth_service: Annotated[AuthService, Depends(Provide["auth_module.auth_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    logout_form: LogoutForm,
    logger: Annotated[Logger, Depends(Provide["auth_module.logger"])],
):
    logger.info(f"user {current_user_id} is logging out...")
    await auth_service.logout(logout_form.access_token, logout_form.refresh_token)
    return BaseResponse[Empty](code=SUCCESS_CODE, data=Empty(), msg="注销成功")


@router.get("/current_user", description="获取当前用户", response_model=BaseResponse[UserViewModel])
@inject
async def current_user(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_service: Annotated[UserService, Depends(Provide["user_module.user_service"])],
):
    user = await user_service.get_user(current_user_id)
    return BaseResponse[UserViewModel](code=SUCCESS_CODE, data=user, msg="获取当前用户成功")
