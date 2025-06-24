from dependency_injector import containers, providers

from llmops_api.service.action import ActionService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    menu_repo = providers.Dependency()
    action_repo = providers.Dependency()
    enforcer = providers.Dependency()

    action_service = providers.Singleton(
        ActionService,
        casbin_enforcer=enforcer,
        action_repo=action_repo,
        menu_repo=menu_repo,
        transaction_factory=db.provided.transaction_session,
        logger=logger.provided.bind.call(name="action-service"),
    )
