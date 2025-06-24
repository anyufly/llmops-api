import uuid

from langchain_core.tools import tool


@tool("generate_uuid")
def generate_uuid():
    """这是一个用于生成uuid的工具"""
    return str(uuid.uuid4())
