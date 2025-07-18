from dependency_injector import containers, providers

from llmops_api.service.document import DocumentService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    document_repo = providers.Dependency()
    knowledge_repo = providers.Dependency()
    document_service = providers.Singleton(
        DocumentService,
        logger=logger.provided.bind.call(name="document-service"),
        transaction_factory=db.provided.transaction_session,
        document_repo=document_repo,
        knowledge_repo=knowledge_repo,
    )
