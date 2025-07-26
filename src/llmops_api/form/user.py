import re
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator
from sqlalchemy import or_
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from llmops_api.base.db.model import User
from llmops_api.base.db.repo import Condition, Paginator


class AddUserForm(BaseModel):
    username: Annotated[str, Field(description="用户名")]
    email: Annotated[Union[EmailStr, Literal[""]], Field(default="", description="用户邮箱")]
    phone: Annotated[str, Field(default="", description="用户手机号")]
    password: Annotated[str, Field(description="用户密码")]
    re_password: Annotated[str, Field(description="重复密码")]

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str):
        pattern = r"^[a-zA-Z0-9_]{5,20}$"

        if re.match(pattern, v):
            return v
        else:
            raise ValueError("用户名必须为数字、字母下划线、组成的5-20位的字符串")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        if v != "":
            pattern = r"^1[3-9]\d{9}$"

            if re.match(pattern, v):
                return v
            else:
                raise ValueError("非法手机号")

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9!@#$%^&*_]{8,20}$"

        if re.match(pattern, v):
            return v
        else:
            raise ValueError(
                "用户密码必须为数字、字母和特殊字符（!@#$%^&*_）组成的8-20位的字符串，其中必须包含至少一个大写字母、一个小写字母和一个数字"
            )

    @field_validator("re_password")
    @classmethod
    def validate_re_password(cls, v: str, info: ValidationInfo):
        if v != info.data["password"]:
            raise ValueError("两次输入的密码不一致")
        else:
            return v

    def convert_to_user(self):
        form_dict = self.model_dump(exclude={"re_password"})
        return User(**form_dict)


class EditUserForm(BaseModel):
    email: Annotated[
        Optional[Union[EmailStr, Literal[""]]], Field(default="", description="用户邮箱")
    ]
    phone: Annotated[Optional[str], Field(default="", description="用户手机号")]

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        if v != "":
            pattern = r"^1[3-9]\d{9}$"

            if re.match(pattern, v):
                return v
            else:
                raise ValueError("非法手机号")

        return v


class UserListQuery(Paginator, Condition):
    query: Annotated[str, Field(default="", description="query")]

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        if self.query != "":
            return [
                or_(
                    User.username.like(f"{self.query}%"),
                    User.phone.like(f"{self.query}%"),
                    User.email.like(f"{self.query}%"),
                )
            ]
        return [True]  # type: ignore
