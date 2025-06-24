from typing import Annotated, Optional

from pydantic import BaseModel, Field

from llmops_api.enum.menu import ActionMethod


class EditActionForm(BaseModel):
    name: Annotated[Optional[str], Field(description="操作名称", default=None)]
    title: Annotated[Optional[str], Field(description="操作标题", default=None)]
    path: Annotated[Optional[str], Field(description="操作对应接口路径", default=None)]
    method: Annotated[Optional[ActionMethod], Field(description="操作对应接口方法", default=None)]
