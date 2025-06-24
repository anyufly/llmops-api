from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Header

from llmops_api.base.exception.biz_error import UnAuthorized
from llmops_api.service.auth import AuthService


@inject
async def get_current_user_id(
    authorization: Annotated[str, Header()],
    auth_service: Annotated[AuthService, Depends(Provide["auth_module.auth_service"])],
):
    if authorization.strip(" ") == "":
        raise UnAuthorized

    user_id = await auth_service.fetch_user_id(authorization)

    return user_id
