from llmops_api.base.db.repo import BaseRepo, SyncBaseRepo
from llmops_api.model.knowledge import KnowledgeDocument


class KnowledgeDocumentRepo(BaseRepo[KnowledgeDocument]):
    pass


class SyncKnowledgeDocumentRepo(SyncBaseRepo[KnowledgeDocument]):
    pass
