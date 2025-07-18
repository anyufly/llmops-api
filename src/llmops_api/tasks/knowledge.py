import io
import sys
from typing import List

from langchain_core.documents.base import Document
from langchain_unstructured import UnstructuredLoader
from pydantic import RootModel
from unstructured.cleaners.core import clean_extra_whitespace
from urlextract import URLExtract

from llmops_api.llm.text_splitter.charater import RecursiveCharacterTextSplitter
from llmops_api.service.document import DocumentFile, DocumentFileSplitConfig


class DocumentFileList(RootModel):
    root: List[DocumentFile]


class DocumentList(RootModel):
    root: List[Document]


@staticmethod
def remove_url_and_email(text: str) -> str:
    # 初始化 URL 提取器
    extractor = URLExtract(extract_email=True)
    urls = extractor.find_urls(text)

    # 删除 URL
    for url in urls:
        text = text.replace(url, "")

    return text


def load_document(self, file: DocumentFile, config: DocumentFileSplitConfig) -> Document:
    post_processors = []

    if config.remove_extra_whitespace:
        post_processors.append(clean_extra_whitespace)

    if config.remove_url_and_email:
        post_processors.append(remove_url_and_email)

    fileStream = io.BytesIO(file.content)

    loader = UnstructuredLoader(
        file=fileStream,
        metadata_filename=file.filename,
        post_processors=post_processors,
        chunking_strategy="basic",
        max_characters=sys.maxsize,
        include_orig_elements=False,
        partition_via_api=False,
    )
    documents = loader.load()
    metadata = (
        {
            "knowledge_id": file.knowledge_id,
            "document_id": file.document_id,
            "filename": file.filename,
        },
    )
    if len(documents) > 1:
        text = "\n\n".join([el.page_content for el in documents])
        document = Document(page_content=text, metadata=metadata)
    else:
        document = Document(
            page_content=documents[0].page_content,
            metadata=metadata,
        )
    return document


def split_document(self, document: Document, config: DocumentFileSplitConfig) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=config.separators if config.separators is None else config.separators.split(","),
        is_separator_regex=config.is_separator_regex,
    )

    return splitter.split_documents(document)


def save_document_chunk(self, knowledge_id: int, document_id: int, documents: List[Document]):
    pass
