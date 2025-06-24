from typing import Annotated, Optional

from pydantic import BaseModel, Field

from llmops_api.model.role import Role


class AddRoleForm(BaseModel):
    name: Annotated[str, Field(description="操作名称")]
    title: Annotated[str, Field(description="操作标题")]

    def to_role(self) -> Role:
        return Role(**self.model_dump())


class EditRoleForm(BaseModel):
    name: Annotated[Optional[str], Field(description="操作名称", default=None)]
    title: Annotated[Optional[str], Field(description="操作标题", default=None)]
