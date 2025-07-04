from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from llmops_api.base.db.model import AutoIncrementID, Base, OperateRecord
from llmops_api.enum.knowledge import RetrievalDataSourceType


class Knowledge(Base, AutoIncrementID, OperateRecord):
    icon: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    describe: Mapped[str] = mapped_column(Text, nullable=False, default="")

    documents: Mapped[List["KnowledgeDocument"]] = relationship(
        back_populates="knowledge",
        primaryjoin="remote(KnowledgeDocument.knowledge_id) == Knowledge.id",
    )


class KnowledgeDocument(Base, AutoIncrementID, OperateRecord):
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    activate_status: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    process_id: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    knowledge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_knowledge.id"),
        nullable=False,
    )
    knowledge: Mapped[Knowledge] = relationship(
        foreign_keys=[knowledge_id],
        back_populates="documents",
        primaryjoin="remote(Knowledge.id) == KnowledgeDocument.knowledge_id",
    )


class RetrievalRecord(Base, AutoIncrementID, OperateRecord):
    data_source_id: Mapped[int] = mapped_column(
        Integer,
    )

    data_source_type: Mapped[RetrievalDataSourceType] = mapped_column(
        Enum(RetrievalDataSourceType),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(Text, nullable=False)

    chunks: Mapped[List["RetrievalRecordChunks"]] = relationship(
        back_populates="record",
        primaryjoin="RetrievalRecord.id == remote(RetrievalRecordChunks.record_id)",
    )


class RetrievalRecordChunks(Base, AutoIncrementID):
    record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_retrieval_record.id"),
        nullable=False,
    )

    record: Mapped[RetrievalRecord] = relationship(
        foreign_keys=[record_id],
        back_populates="documents",
        primaryjoin="remote(RetrievalRecord.id) == RetrievalRecordChunks.record_id",
    )

    # 向量数据库中的ID
    chunk_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # 被召回时的文本
    chunck_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_knowledge_document.id"),
        nullable=False,
    )

    document: Mapped["KnowledgeDocument"] = relationship(
        primaryjoin="remote(KnowledgeDocument.id) == RetrievalRecordChunks.document_id",
    )

    knowledge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_knowledge.id"),
        nullable=False,
    )

    knowledge: Mapped[Knowledge] = relationship(
        foreign_keys=[knowledge_id],
        back_populates="documents",
        primaryjoin="remote(Knowledge.id) == RetrievalRecordChunks.knowledge_id",
    )

    score: Mapped[Decimal] = mapped_column(Numeric(7, 6), nullable=False)
