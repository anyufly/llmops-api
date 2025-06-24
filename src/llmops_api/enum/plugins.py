from llmops_api.base.enum import LabeledEnum


class PluginType(LabeledEnum):
    reserved = ("reserved", "内置插件")
    custom = ("custom", "自定义插件")
