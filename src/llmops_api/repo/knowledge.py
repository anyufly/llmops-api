from llmops_api.base.db.repo import BaseRepo
from llmops_api.model.knowledge import Knowledge


class KnowledgeRepo(BaseRepo[Knowledge]):
    pass


class SyncKnowledgeRepo(BaseRepo[Knowledge]):
    pass
