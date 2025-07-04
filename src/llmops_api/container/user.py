from dependency_injector import containers, providers

from llmops_api.repo.user import UserRepo
from llmops_api.service.user import UserService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    repo = providers.Singleton(UserRepo, logger=logger.provided.bind.call(name="user-repo"))
    user_service = providers.Singleton(
        UserService,
        repo=repo,
        transaction_factory=db.provided.transaction_session,
        logger=logger.provided.bind.call(name="user-service"),
    )
