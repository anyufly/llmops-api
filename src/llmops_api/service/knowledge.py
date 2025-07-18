from contextlib import AbstractAsyncContextManager
from typing import Callable

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession


class KnowledgeService:
    def __init__(
        self,
        logger: Logger,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self.logger = logger
        self.transaction_factory = transaction_factory

    def create_knowledge(self):
        pass

    def edit_knowledge(self):
        pass

    def delete_knowledge(self):
        pass

    def get_knowledge(self):
        pass

    def knowledge_list(self):
        pass
