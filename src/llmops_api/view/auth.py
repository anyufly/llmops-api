from typing import Annotated

from pydantic import BaseModel, Field


class TokensViewModel(BaseModel):
    access_token: Annotated[str, Field(description="访问token")]
    refresh_token: Annotated[str, Field(description="刷新token")]
