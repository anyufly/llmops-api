from fastapi import status

from llmops_api.base.exception.biz_error import BizError

MenuNotExists = BizError(
    code="MenuNotExists", status_code=status.HTTP_404_NOT_FOUND, msg="菜单不存在"
)

ParentMenuNotExists = BizError(
    code="ParentMenuNotExists", status_code=status.HTTP_404_NOT_FOUND, msg="父菜单不存在"
)

MenuHasChild = BizError(
    code="MenuHasChild",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    msg="该菜单下存在子菜单，无法删除",
)

MenuHasAction = BizError(
    code="MenuHasAction",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    msg="该菜单下存在已配置的操作，无法删除",
)

MenuNameExists = BizError(
    code="MenuNameExists",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    msg="菜单名称已存在",
)
