from fastapi import status

from llmops_api.base.exception.biz_error import BizError

UsernameOrPasswordWrong = BizError(code="UsernameOrPasswordWrong", msg="用户名或密码错误")
AccessTokenExpire = BizError(
    code="AccessTokenExpire", msg="access_token已过期", status_code=status.HTTP_401_UNAUTHORIZED
)

AccessTokenNotExpire = BizError(
    code="AccessTokenNotExpire",
    msg="access_token未过期",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
)


RefreshTokenExpire = BizError(
    code="RefreshTokenExpire",
    msg="refresh_token已过期,请重新登录",
    status_code=status.HTTP_401_UNAUTHORIZED,
)

OldPasswordWrong = BizError(code="OldPasswordWrong", msg="旧密码错误")
