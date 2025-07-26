from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from fastapi.routing import APIRoute

from llmops_api.base.exception.biz_error import Forbidden
from llmops_api.depends.auth import get_current_user_id
from llmops_api.service.permissions import PermissionsService


@inject
async def need_permission(
    request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
    permission_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
):
    # 从请求的scope中获取路由对象
    route: APIRoute = request.scope.get("route")  # type: ignore

    path = route.path
    method = request.method.upper()

    has_permission_for_user = await permission_service.has_permission(user_id, path, method)

    if not has_permission_for_user:
        raise Forbidden
    return user_id
