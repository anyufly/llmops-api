import importlib
from typing import Any

import msgpack
from kombu.serialization import register
from pydantic import BaseModel, RootModel


def get_import_path(obj) -> tuple[Any, Any | None]:
    # 获取对象所属的模块名
    module = obj.__module__
    # 获取对象的类名或函数名
    name = getattr(obj, "__qualname__", getattr(obj, "__name__", repr(obj)))
    # 组合成完整导入路径
    return module, name


def default(obj):
    if isinstance(obj, BaseModel):
        module, name = get_import_path(type(obj))
        return {
            "__pydantic__": True,
            "data": obj.model_dump(),
            "module": module,
            "name": name,
        }
    return obj


def decode(obj):
    if "__pydantic__" in obj:
        module = obj["module"]
        name = obj["name"]
        data = obj["data"]
        m = importlib.import_module(module)
        model_class = getattr(m, name)

        if issubclass(model_class, RootModel):
            return model_class(root=data)
        else:
            return model_class(**data)
    return obj


def serialize(obj):
    return msgpack.packb(obj, use_bin_type=True, default=default)


def deserialize(data):
    return msgpack.unpackb(data, raw=False, object_hook=decode)


def register_msgpack_with_pydantic():
    register(
        "msgpack-pydantic",
        serialize,
        deserialize,
        content_type="application/x-msgpack-pydantic",
        content_encoding="binary",
    )
