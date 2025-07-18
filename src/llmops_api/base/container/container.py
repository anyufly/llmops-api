from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from llmops_api.base.casbin.adapter import CasbinAdapter
from llmops_api.base.casbin.enforcer import new_casbin_enforcer
from llmops_api.base.casbin.watcher import new_watcher
from llmops_api.base.config import load_config
from llmops_api.base.db.engine import Database, SyncDatabase
from llmops_api.base.logger import init_logger
from llmops_api.base.redis.pool import Redis
from llmops_api.container.action import Container as ActionContainer
from llmops_api.container.auth import Container as AuthContainer
from llmops_api.container.document import Container as DocumentContainer
from llmops_api.container.knowledge import Container as KnowledgeContainer
from llmops_api.container.menu import Container as MenuContainer
from llmops_api.container.permissions import Container as PermissionsContainer
from llmops_api.container.role import Container as RoleContainer
from llmops_api.container.user import Container as UserContainer
from llmops_api.repo.action import ActionRepo
from llmops_api.repo.document import KnowledgeDocumentRepo, SyncKnowledgeDocumentRepo
from llmops_api.repo.knowledge import KnowledgeRepo, SyncKnowledgeRepo
from llmops_api.repo.menu import MenuRepo


class CeleryContainer(DeclarativeContainer):
    config = providers.Singleton(load_config)
    db = providers.Singleton(Database, config=config.provided.database)
    sync_db = providers.Singleton(SyncDatabase, config=config.provided.database)
    logger = providers.Singleton(
        init_logger, level=config.provided.logger.level, debug=config.provided.env.debug_mode
    )

    sync_knowledge_repo = providers.Singleton(
        SyncKnowledgeRepo, logger=logger.provided.bind.call(name="sync-knowledge-repo")
    )

    sync_document_repo = providers.Singleton(
        SyncKnowledgeDocumentRepo, logger=logger.provided.bind.call(name="sync-document-repo")
    )


class ApplicationContainer(DeclarativeContainer):
    config = providers.Singleton(load_config)
    db = providers.Singleton(Database, config=config.provided.database)
    sync_db = providers.Singleton(SyncDatabase, config=config.provided.database)
    logger = providers.Singleton(
        init_logger, level=config.provided.logger.level, debug=config.provided.env.debug_mode
    )

    redis = providers.Singleton(Redis, config=config.provided.redis)

    casbin_watcher = providers.Singleton(
        new_watcher,
        publish_client_factory=redis.provided.client,
        logger=logger.provided.bind.call(name="casbin-watcher"),
    )

    casbin_adapter = providers.Singleton(
        CasbinAdapter, transaction_factory=db.provided.transaction_session
    )

    casbin_enforcer = providers.Singleton(
        new_casbin_enforcer,
        adapter=casbin_adapter,
        watcher=casbin_watcher,
        logger=logger.provided.bind.call(name="casbin-enforcer"),
    )

    user_module = providers.Container(
        UserContainer,
        db=db,
        logger=logger.provided.bind.call(name="user-module"),
    )

    menu_repo = providers.Singleton(MenuRepo, logger=logger.provided.bind.call(name="menu-repo"))
    action_repo = providers.Singleton(
        ActionRepo, logger=logger.provided.bind.call(name="action-repo")
    )

    menu_module = providers.Container(
        MenuContainer,
        db=db,
        menu_repo=menu_repo,
        action_repo=action_repo,
        logger=logger.provided.bind.call(name="menu-module"),
    )

    action_module = providers.Container(
        ActionContainer,
        db=db,
        logger=logger.provided.bind.call(name="action-module"),
        menu_repo=menu_repo,
        action_repo=action_repo,
        enforcer=casbin_enforcer,
    )

    role_module = providers.Container(
        RoleContainer,
        db=db,
        logger=logger.provided.bind.call(name="role-module"),
        enforcer=casbin_enforcer,
    )

    auth_module = providers.Container(
        AuthContainer,
        db=db,
        redis=redis,
        logger=logger.provided.bind.call(name="auth-module"),
        repo=user_module.container.repo,
        auth_config=config.provided.auth,
    )

    permissions_module = providers.Container(
        PermissionsContainer,
        db=db,
        redis=redis,
        logger=logger.provided.bind.call(name="permissions-module"),
        enforcer=casbin_enforcer,
        menu_repo=menu_repo,
        action_repo=action_repo,
        user_repo=user_module.container.repo,
        role_repo=role_module.container.repo,
    )

    knowledge_repo = providers.Singleton(
        KnowledgeRepo, logger=logger.provided.bind.call(name="knowledge-repo")
    )

    document_repo = providers.Singleton(
        KnowledgeDocumentRepo, logger=logger.provided.bind.call(name="document-repo")
    )

    knowledge_module = providers.Container(
        KnowledgeContainer,
        db=db,
        logger=logger.provided.bind.call(name="knowledge-module"),
    )

    document_module = providers.Container(
        DocumentContainer,
        db=db,
        document_repo=document_repo,
        knowledge_repo=knowledge_repo,
        logger=logger.provided.bind.call(name="document-module"),
    )


def init_container():
    container = ApplicationContainer()
    container.wire(
        packages=[
            "llmops_api.api",
            "llmops_api.depends",
        ],
    )
    return container


def init_celery_container():
    return CeleryContainer()
