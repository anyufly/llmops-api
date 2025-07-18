from dependency_injector import containers, providers

from llmops_api.service.knowledge import KnowledgeService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    knowledge_service = providers.Singleton(
        KnowledgeService,
        logger=logger.provided.bind.call(name="knowledge-service"),
        transaction_factory=db.provided.transaction_session,
    )
