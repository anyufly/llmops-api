from llmops_api.base.db.repo import BaseRepo, Condition, SyncBaseRepo
from llmops_api.model.knowledge import Knowledge, KnowledgeDocument


class KnowledgeDocumentRepo(BaseRepo[KnowledgeDocument]):
    pass


class SyncKnowledgeDocumentRepo(SyncBaseRepo[KnowledgeDocumentRepo]):
    pass
