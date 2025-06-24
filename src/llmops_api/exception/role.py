from fastapi import status

from llmops_api.base.exception.biz_error import BizError

RoleNotExists = BizError(
    code="RoleNotExists",
    msg="角色不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)

RoleNameExists = BizError(
    code="RoleNameExists",
    msg="角色名称已存在",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)

RoleHasUsers = BizError(
    code="RoleHasUsers",
    msg="该角色下存在用户，无法删除",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
