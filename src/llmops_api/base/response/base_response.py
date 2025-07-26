from typing import Annotated, Any, Generic, List

from pydantic import BaseModel, Field
from typing_extensions import TypeVar


class Empty(BaseModel):
    pass


DataT = TypeVar("DataT", default=Empty)


class BaseResponse(BaseModel, Generic[DataT]):
    code: Annotated[str, Field(title="code", description="业务状态码")]
    data: Annotated[DataT, Field(title="data", description="数据")]
    msg: Annotated[str, Field(title="msg", description="消息")]


class ValidateErrorInfo(BaseModel):
    loc: Annotated[List[str], Field(title="loc", description="校验未通过字段路径")]
    input: Annotated[Any, Field(title="input", description="校验未通过字段的输入值")]
    reason: Annotated[str, Field(title="input", description="校验未通过理由")]


class ValidateErrorData(BaseModel):
    errors: Annotated[
        List[ValidateErrorInfo], Field(title="input", description="校验未通过错误列表")
    ]


ValidateErrorResponse = BaseResponse[ValidateErrorData]
ServerInternalErrorResponse = BaseResponse[Empty]
ForbiddenResponse = BaseResponse[Empty]
UnAuthorizedResponse = BaseResponse[Empty]
NotFoundResponse = BaseResponse[Empty]
