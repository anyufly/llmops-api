from dependency_injector import containers, providers

from llmops_api.repo.role import RoleRepo
from llmops_api.service.role import RoleService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    enforcer = providers.Dependency()

    repo = providers.Singleton(
        RoleRepo,
        logger=logger.provided.bind.call(name="role-repo"),
    )
    role_service = providers.Singleton(
        RoleService,
        repo=repo,
        enforcer=enforcer,
        transaction_factory=db.provided.transaction_session,
        logger=logger.provided.bind.call(name="role-service"),
    )
