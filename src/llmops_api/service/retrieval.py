from contextlib import AbstractAsyncContextManager
from typing import Callable, Optional

from loguru._logger import Logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from llmops_api.enum.knowledge import RetrievalMode


class RetrievalConfig(BaseModel):
    pass


class RetrievalService:
    def __init__(
        self,
        logger: Logger,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self.logger = logger
        self.transaction_factory = transaction_factory

    def retrieval(
        self,
        knowledge_id: str,
        query: str,
        mode: RetrievalMode,
        retrieval_config: RetrievalConfig,
        data_source_id: Optional[int] = None,
    ):
        pass

    def retrieval_record_list(
        self,
        knowledge_id: str,
    ):
        pass
