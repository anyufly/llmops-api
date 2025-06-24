import datetime
from typing import Annotated, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from llmops_api.base.view.relation import Relation


class OperatorModel(BaseModel):
    id: Annotated[int, Field(description="用户ID")]
    username: Annotated[str, Field(description="用户名")]


class OperatorRecordModel(BaseModel):
    create_at: Annotated[
        Optional[datetime.datetime],
        Field(default=None, description="创建时间"),
    ]
    creator: Annotated[
        Optional[OperatorModel],
        Field(description="创建人", default=None),
        Relation(
            pydantic_model=OperatorModel,
        ),
    ]
    update_at: Annotated[
        Optional[datetime.datetime],
        Field(default=None, description="更新时间"),
    ]
    updator: Annotated[
        Optional[OperatorModel],
        Field(description="更新人", default=None),
        Relation(
            pydantic_model=OperatorModel,
        ),
    ]


ViewModelT = TypeVar("ViewModelT", bound=BaseModel)


class ListViewModel(BaseModel, Generic[ViewModelT]):
    items: Annotated[List[ViewModelT], Field(default_factory=list, description="数据列表")]


class PaginationListViewModel(BaseModel, Generic[ViewModelT]):
    items: Annotated[List[ViewModelT], Field(default_factory=list, description="数据列表")]
    page: Annotated[int, Field(description="页码")]
    page_size: Annotated[int, Field(description="页长")]
    total: Annotated[int, Field(description="数据总长度")]
