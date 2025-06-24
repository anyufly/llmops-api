from typing import Annotated

from pydantic import BaseModel, Field

from llmops_api.enum.menu import ActionMethod
from llmops_api.model.menu import Action


class AddMenuActionForm(BaseModel):
    name: Annotated[str, Field(description="操作名称")]
    title: Annotated[str, Field(description="操作标题")]
    path: Annotated[str, Field(description="操作对应接口路径")]
    method: Annotated[ActionMethod, Field(description="操作对应接口方法")]

    def to_action(self) -> Action:
        return Action(**self.model_dump())
