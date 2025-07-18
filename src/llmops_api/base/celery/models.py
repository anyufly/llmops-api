from pydantic import BaseModel,RootModel, Field
from typing import Optional, List
from langchain_core.documents.base import Document

class DocumentFile(BaseModel):
    knowledge_id: int
    document_id: Optional[int] = Field(default=None)
    filename: str
    content: bytes


class DocumentFileSplitConfig(BaseModel):
    separators: Optional[str] = Field(default=None)
    chunk_size: Optional[int] = Field(default=None, ge=100)
    chunk_overlap: Optional[int] = Field(default=None, ge=0)
    remove_extra_whitespace: bool = False
    remove_url_and_email: bool = False
    is_separator_regex: bool = False


class DocumentFileList(RootModel):
    root: List[DocumentFile]


class DocumentList(RootModel):
    root: List[Document]