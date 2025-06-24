import random

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RadomIntArgsSchema(BaseModel):
    start: int = Field(description="表示随机整数生成区间的开始整数")
    end: int = Field(description="表示随机整数生成区间的结束整数")


@tool("random_int", args_schema=RadomIntArgsSchema)
def random_int(start: int, end: int) -> int:
    """
    这是一个用于生成[start,end]之间（包含start和end）随机整数的工具。
    """
    random.randint()
