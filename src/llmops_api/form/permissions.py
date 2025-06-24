from typing import Annotated

from pydantic import BaseModel, Field


class AddUserRoleForm(BaseModel):
    user_id: Annotated[int, Field(description="用户ID")]
    role_id: Annotated[int, Field(description="角色ID")]


class DeleteUserRoleForm(AddUserRoleForm):
    pass


class AddRoleActionForm(BaseModel):
    role_id: Annotated[int, Field(description="角色ID")]
    action_id: Annotated[int, Field(description="操作ID")]


class DeleteRoleActionForm(AddRoleActionForm):
    pass
