from typing import Annotated

from pydantic import Field

from llmops_api.base.view.model import OperatorRecordModel


class UserViewModel(OperatorRecordModel):
    id: Annotated[
        int,
        Field(description="用户ID"),
    ]
    username: Annotated[
        str,
        Field(description="用户名"),
    ]
    email: Annotated[
        str,
        Field(description="用户邮箱"),
    ]
    phone: Annotated[
        str,
        Field(description="用户手机号"),
    ]
