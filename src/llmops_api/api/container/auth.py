from dependency_injector import containers, providers

from llmops_api.service.auth import AuthService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    redis = providers.Dependency()
    logger = providers.Dependency()
    repo = providers.Dependency()
    auth_config = providers.Dependency()
    auth_service = providers.Singleton(
        AuthService,
        repo=repo,
        transaction_factory=db.provided.transaction_session,
        redis_client_factory=redis.provided.client,
        logger=logger.provided.bind.call(name="user-service"),
        auth_config=auth_config,
    )
