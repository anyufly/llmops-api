from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class BizError(Exception):
    code: str
    msg: str
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    data: dict[str, Any] = {}

    def __init__(self, code: str, msg: str, status_code: int = 500, data: dict[str, Any] = {}):
        self.code = code
        self.msg = msg
        self.status_code = status_code
        self.data = data
        super().__init__(self.msg)

    @classmethod
    def from_validation_error(cls, err: RequestValidationError) -> "BizError":
        errors = err.errors()
        data = []

        for err in errors:
            data.append(
                {
                    "loc": err.get("loc", ""),
                    "input": err.get("input", ""),
                    "reason": err.get("msg", ""),
                }
            )
        return BadRequest.with_data({"errors": data})

    @classmethod
    def from_http_exception(cls, err: StarletteHTTPException) -> "BizError":
        return ServerInternalError.with_status_code(err.status_code).with_msg(err.detail)

    @classmethod
    def from_exception(cls, err: BaseException) -> "BizError":
        return ServerInternalError.with_msg(str(err))

    def with_data(self, data: dict[str, Any]):
        cloned = self.__class__(
            code=self.code, msg=self.msg, data=data, status_code=self.status_code
        )
        return cloned

    def with_status_code(self, status_code: int):
        cloned = self.__class__(
            code=self.code, msg=self.msg, data=self.data, status_code=status_code
        )
        return cloned

    def with_msg(self, msg: str):
        cloned = self.__class__(
            code=self.code, msg=msg, data=self.data, status_code=self.status_code
        )
        return cloned

    def json_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"code": self.code, "msg": self.msg, "data": jsonable_encoder(self.data)},
        )


ServerInternalError = BizError(code="ServerInternalError", msg="未知错误")
NotFound = BizError(code="NotFound", status_code=status.HTTP_404_NOT_FOUND, msg="资源未找到")
Forbidden = BizError(code="Forbidden", status_code=status.HTTP_403_FORBIDDEN, msg="没有权限")
BadRequest = BizError(code="BadRequest", status_code=status.HTTP_400_BAD_REQUEST, msg="非法参数")
UnAuthorized = BizError(
    code="UnAuthorized", status_code=status.HTTP_401_UNAUTHORIZED, msg="身份验证未通过"
)
