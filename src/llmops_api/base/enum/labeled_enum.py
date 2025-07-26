from enum import Enum
from typing import Any


class BaseEnum(Enum):
    @classmethod
    def load(cls, value: Any):
        """
        通过值获取枚举成员

        :param value: 枚举项的值
        :return 配的枚举成员
        :raise ValueError 找不到匹配的枚举成员时
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"值 '{value}' 在枚举 {cls.__name__} 中未找到")

    @classmethod
    def load_by_name(cls, name: str):
        """
        通过枚举项的名称获取枚举成员

        :param name:枚举项的名称（字符串）
        :return 匹配的枚举成员
        :raise ValueError 找不到匹配的枚举成员时
        """
        for member in cls:
            if member.name == name:
                return member
        raise ValueError(f"名称 '{name}' 在枚举 {cls.__name__} 中未找到")


class LabeledEnum(BaseEnum):
    """
    带标签的枚举基类，每个枚举项包含value和label属性。
    label用于描述枚举项，可通过to_dict_list方法转换为字典数组。
    """

    def __init__(self, value: Any, label: str):
        """
        初始化枚举项，保存value和label
        :param value: 枚举项的值
        :param label: 枚举项的标签描述
        """
        self._value_ = value
        self.label = label

    @classmethod
    def to_dict_list(cls):
        """
        将枚举的所有项转换为字典数组
        每个字典包含'value'和'label'两个键
        :return: 包含所有枚举项字典的列表
        """
        return [{"label": member.label, "value": member.value} for member in cls]
