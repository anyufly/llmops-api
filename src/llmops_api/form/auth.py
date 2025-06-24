import re
from typing import Annotated, Any

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator


class LoginForm(BaseModel):
    username: Annotated[str, Field(description="用户名")]
    password: Annotated[str, Field(description="密码")]


class LogoutForm(BaseModel):
    access_token: Annotated[str, Field(description="访问token")]
    refresh_token: Annotated[str, Field(description="刷新token")]


class RefreshTokenForm(BaseModel):
    access_token: Annotated[str, Field(description="访问token")]
    refresh_token: Annotated[str, Field(description="刷新token")]


class ChangePassForm(BaseModel):
    old_password: Annotated[str, Field(description="旧密码")]
    new_password: Annotated[str, Field(description="用户密码")]
    re_password: Annotated[str, Field(description="重复密码")]

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str, info: ValidationInfo):
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9!@#$%^&*_]{8,20}$"

        if re.match(pattern, v):
            if v == info.data["old_password"]:
                raise ValueError("新密码不能与旧密码一致")
            return v
        else:
            raise ValueError(
                "用户密码必须为数字、字母和特殊字符（!@#$%^&*_）组成的8-20位的字符串，其中必须包含至少一个大写字母、一个小写字母和一个数字"
            )

    @model_validator(mode="before")
    @classmethod
    def validate_re_password(cls, data: Any):
        if not isinstance(data, dict):
            return data

        if data.get("re_password") != data.get("new_password"):
            raise ValueError("两次输入的密码不一致")

        return data
