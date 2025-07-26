from typing import Any, Callable, Coroutine, Dict, Type, Union

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from llmops_api.base.exception.biz_error import BizError
from llmops_api.base.exception.error_response import ErrorResponse


async def validation_error_handeler(request: Request, exc: RequestValidationError):
    return ErrorResponse(error=exc).json_response()


async def http_exception_handeler(request: Request, exc: StarletteHTTPException):
    return ErrorResponse(error=exc).json_response()


async def biz_error_handeler(request: Request, exc: BizError):
    return ErrorResponse(error=exc).json_response()


async def exception_handeler(request: Request, exc: Exception):
    return ErrorResponse(error=exc).json_response()


error_handlers: Dict[
    Union[int, Type[Exception]],
    Callable[[Request, Any], Coroutine[Any, Any, Response]],
] = {
    RequestValidationError: validation_error_handeler,
    StarletteHTTPException: http_exception_handeler,
    BizError: biz_error_handeler,
    Exception: exception_handeler,
}
