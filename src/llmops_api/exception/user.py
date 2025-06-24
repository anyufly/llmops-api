from fastapi import status

from llmops_api.base.exception.biz_error import BizError

UsernameExists = BizError(
    code="UsernameExists",
    msg="用户名已存在",
)

UserNotExists = BizError(
    code="UserNotExists",
    msg="用户不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)
