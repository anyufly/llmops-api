from datetime import datetime

from langchain_core.tools import tool


@tool("current")
def current():
    """
    这是一个用于获取当前时间的工具
    """
    return datetime.now()
