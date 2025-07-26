from typing import Any, Dict

from fastapi import status

from llmops_api.base.response.base_response import (
    ForbiddenResponse,
    NotFoundResponse,
    ServerInternalErrorResponse,
    UnAuthorizedResponse,
    ValidateErrorResponse,
)

responses: Dict[int | str, Dict[str, Any]] = {
    "default": {},
    status.HTTP_400_BAD_REQUEST: {
        "model": ValidateErrorResponse,
        "description": "参数验证失败",
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": ServerInternalErrorResponse,
        "description": "内部错误",
    },
    status.HTTP_404_NOT_FOUND: {
        "model": NotFoundResponse,
        "description": "资源不存在",
    },
    status.HTTP_403_FORBIDDEN: {"model": ForbiddenResponse, "description": "没有权限"},
    status.HTTP_401_UNAUTHORIZED: {
        "model": UnAuthorizedResponse,
        "description": "身份验证失败",
    },
}
