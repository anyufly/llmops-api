from llmops_api.base.enum.labeled_enum import BaseEnum, LabeledEnum


class MenuType(LabeledEnum):
    default = ("default", "")
    discover = ("discover", "探索")
    manage = ("manage", "管理")


class ActionMethod(BaseEnum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"
    options = "OPTIONS"
    head = "HEAD"
