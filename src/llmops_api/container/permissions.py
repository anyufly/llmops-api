from dependency_injector import containers, providers

from llmops_api.service.permissions import PermissionsService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    redis = providers.Dependency()
    logger = providers.Dependency()
    enforcer = providers.Dependency()
    menu_repo = providers.Dependency()
    action_repo = providers.Dependency()
    user_repo = providers.Dependency()
    role_repo = providers.Dependency()

    permissions_service = providers.Singleton(
        PermissionsService,
        casbin_enforcer=enforcer,
        menu_repo=menu_repo,
        action_repo=action_repo,
        user_repo=user_repo,
        role_repo=role_repo,
        transaction_factory=db.provided.transaction_session,
        logger=logger.provided.bind.call(name="permissions-service"),
    )
