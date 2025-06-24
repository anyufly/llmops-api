from dependency_injector import containers, providers

from llmops_api.service.menu import MenuService


class Container(containers.DeclarativeContainer):
    db = providers.Dependency()
    logger = providers.Dependency()
    menu_repo = providers.Dependency()
    action_repo = providers.Dependency()
    menu_service = providers.Singleton(
        MenuService,
        menu_repo=menu_repo,
        action_repo=action_repo,
        transaction_factory=db.provided.transaction_session,
        logger=logger.provided.bind.call(name="menu-service"),
    )
