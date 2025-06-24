from typing import Annotated

from pydantic import Field

from llmops_api.base.view.model import OperatorRecordModel


class RoleViewModel(OperatorRecordModel):
    id: Annotated[
        int,
        Field(description="角色ID"),
    ]

    name: Annotated[
        str,
        Field(description="角色名称"),
    ]

    title: Annotated[
        str,
        Field(description="角色标题"),
    ]
