from fastapi import status

from llmops_api.base.exception.biz_error import BizError

ActionNotExists = BizError(
    code="ActionNotExists", msg="操作不存在", status_code=status.HTTP_404_NOT_FOUND
)

ActionNameExists = BizError(
    code="ActionNameExists", msg="操作名已存在", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
)

ActionInUse = BizError(
    code="ActionInUse",
    msg="存在有该操作权限的用户或角色，无法删除",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)
