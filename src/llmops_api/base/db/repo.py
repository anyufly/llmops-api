import datetime
from abc import ABC, abstractmethod
from typing import (
    Annotated,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
)

from loguru._logger import Logger
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument, _ColumnExpressionOrStrLabelArgument
from sqlalchemy.sql.base import ExecutableOption, _NoArg

from llmops_api.base.db.model import AutoIncrementID, Base, SoftDelete


class Condition(ABC):
    @abstractmethod
    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        raise NotImplementedError("to_condition not implement")


class Paginator(BaseModel):
    page: Annotated[
        int,
        Field(default=1, ge=1, description="页码"),
    ]
    page_size: Annotated[
        int,
        Field(default=20, ge=1, description="页长"),
    ]


class QueryConfig:
    def __init__(
        self,
        *,
        options: List[ExecutableOption] = [],
        condition: Optional[Condition] = None,
        paginator: Optional[Paginator] = None,
        order_by: List[
            Union[
                Literal[None, _NoArg.NO_ARG],
                _ColumnExpressionOrStrLabelArgument[Any],
            ]
        ] = [],
    ):
        self.options = options
        self.condition = condition
        self.paginator = paginator
        self.order_by = order_by


ModelT = TypeVar("ModelT", bound=Base)

T = TypeVar("T")


class RepoException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseRepo(Generic[ModelT]):
    def __init__(self, logger: Logger):
        self.logger = logger

    def _check_type_arg(self) -> None:
        self._type_arg = None
        for base in getattr(self, "__orig_bases__", []):
            if args := get_args(base):
                self._type_arg = args[0]
        if self._type_arg is None:
            raise TypeError("No generic type found")

    async def add(self, session: AsyncSession, model: ModelT) -> None:
        self._check_type_arg()

        session.add(model)
        await session.flush()

    async def insert(self, session: AsyncSession, **kwargs) -> None:
        self._check_type_arg()
        await session.execute(insert(self._type_arg).values(**kwargs))

    async def exists_when(self, session: AsyncSession, condition: Condition) -> bool:
        self._check_type_arg()

        stmt = select(func.count("*")).where(*condition.to_condition())
        if issubclass(self._type_arg, SoftDelete):
            stmt = stmt.where(self._type_arg.delete_at.is_(None))
        count = await session.scalar(stmt)

        return count > 0

    async def exists(self, session: AsyncSession, id: int) -> bool:
        self._check_type_arg()

        if id <= 0:
            raise ValueError("id must be positive")

        if issubclass(self._type_arg, AutoIncrementID):
            stmt = select(func.count(self._type_arg.id)).where(self._type_arg.id == id)

            if issubclass(self._type_arg, SoftDelete):
                stmt = stmt.where(self._type_arg.delete_at.is_(None))

            count = await session.scalar(stmt)
            return count > 0
        else:
            raise RepoException("only support the model that extends AutoIncrementID")

    async def get_by_id(
        self,
        session: AsyncSession,
        id: int,
        *,
        options: List[ExecutableOption] = [],
    ) -> ModelT:
        self._check_type_arg()

        if id <= 0:
            raise ValueError("id must be positive")

        if issubclass(self._type_arg, AutoIncrementID):
            stmt = select(self._type_arg)

            if len(options) > 0:
                stmt = stmt.options(*options)
            stmt = stmt.where(self._type_arg.id == id)
            if issubclass(self._type_arg, SoftDelete):
                stmt = stmt.where(self._type_arg.delete_at.is_(None))

            result = await session.scalars(stmt)
            return result.one_or_none()
        else:
            raise RepoException("only support the model that extends AutoIncrementID")

    async def update_by_id(self, session: AsyncSession, id: int, **kwargs: Any) -> None:
        self._check_type_arg()
        await session.execute(
            update(self._type_arg).where(self._type_arg.id == id).values(**kwargs)
        )

    async def fetch_list(
        self,
        session: AsyncSession,
        query_config: QueryConfig,
    ) -> Tuple[Optional[int], List[ModelT]]:
        self._check_type_arg()

        stmt = select(self._type_arg)

        if len(query_config.options) > 0:
            stmt = stmt.options(*query_config.options)

        if query_config.paginator is not None:
            count_stmt = select(func.count("*"))
            if query_config.condition is not None:
                count_stmt = count_stmt.where(*query_config.condition.to_condition())
                stmt = stmt.where(*query_config.condition.to_condition())

            if issubclass(self._type_arg, SoftDelete):
                count_stmt = count_stmt.where(self._type_arg.delete_at.is_(None))
                stmt = stmt.where(self._type_arg.delete_at.is_(None))

            count = await session.scalar(count_stmt)
            model_list = []
            if count > 0:
                stmt = stmt.offset(
                    query_config.paginator.page_size * (query_config.paginator.page - 1)
                ).limit(query_config.paginator.page_size)
                if len(query_config.order_by) > 0:
                    stmt = stmt.order_by(*query_config.order_by)
                model_list = await session.scalars(stmt)
            return count, list(model_list)
        else:
            if query_config.condition is not None:
                stmt = stmt.where(*query_config.condition.to_condition())

            if issubclass(self._type_arg, SoftDelete):
                stmt = stmt.where(self._type_arg.delete_at.is_(None))

            if len(query_config.order_by) > 0:
                stmt = stmt.order_by(*query_config.order_by)
            model_list = await session.scalars(stmt)
            return None, list(model_list)

    async def remove_by_id(
        self, session: AsyncSession, id: int, delete_by: Optional[int] = None
    ) -> None:
        self._check_type_arg()

        if issubclass(self._type_arg, SoftDelete):
            values = {"delete_at": datetime.datetime.now()}

            if delete_by is not None:
                values.update({"delete_by": delete_by})
            await session.execute(
                update(self._type_arg).where(self._type_arg.id == id).values(**values)
            )
        else:
            await session.execute(delete(self._type_arg).where(self._type_arg.id == id))
