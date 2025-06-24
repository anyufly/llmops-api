from dataclasses import dataclass

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from llmops_api.base.exception.biz_error import BizError


@dataclass
class ErrorResponse:
    error: Exception

    def json_response(self) -> JSONResponse:
        bizError = None
        if isinstance(self.error, RequestValidationError):
            bizError = BizError.from_validation_error(self.error)
        elif isinstance(self.error, StarletteHTTPException):
            bizError = BizError.from_http_exception(self.error)
        elif isinstance(self.error, BizError):
            bizError = self.error
        else:
            bizError = BizError.from_exception(self.error)

        return bizError.json_response()
