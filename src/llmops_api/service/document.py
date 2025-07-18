from contextlib import AbstractAsyncContextManager
from typing import Callable, List, Optional

from loguru._logger import Logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from llmops_api.repo.document import KnowledgeDocumentRepo
from llmops_api.repo.knowledge import KnowledgeRepo


class DocumentFile(BaseModel):
    knowledge_id: int
    document_id: Optional[int]
    filename: str
    content: bytes


class DocumentFileSplitConfig(BaseModel):
    separators: Optional[str] = Field(default=None)
    chunk_size: Optional[int] = Field(default=None, ge=100)
    chunk_overlap: Optional[int] = Field(default=None, ge=0)
    remove_extra_whitespace: bool = False
    remove_url_and_email: bool = False
    is_separator_regex: bool = False


# DEFAULT_DOCUMENT_FILE_SPLIT_CONFIG = DocumentFileSplitConfig(
#     separators="",
#     chunk_size=2000,
#     chunk_overlap=200,
#     remove_extra_whitespace=True,
#     remove_url_and_email=False,
#     is_separator_regex=False,
# )


class DocumentService:
    def __init__(
        self,
        logger: Logger,
        knowledge_repo: KnowledgeRepo,
        document_repo: KnowledgeDocumentRepo,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self.logger = logger
        self.transaction_factory = transaction_factory
        self.knowledge_repo = knowledge_repo
        self.document_repo = document_repo

    async def create_documents(
        self, user_id: int, document_files: List[DocumentFile]
    ) -> List[DocumentFile]:
        async with self.transaction_factory() as session:
            pass
        pass

    def document_list(self, knowledge_id: int):
        pass

    async def rename_document(self, document_id: int):
        pass

    def delete_document(self, document_id: int):
        pass

    def toogle_activate(self, document_id: int):
        pass

    def get_document_chunks(self, document_id: int):
        pass

    def edit_document_chunk(self, chunk_id: int):
        pass

    def delete_document_chunk(self, chunk_id: int):
        pass
