import asyncio
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import false, pool, text, true
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from llmops_api.base.config import DatabaseConfig

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def has_extra_flag(flag: str):
    if config.cmd_opts.x is not None:  # type: ignore
        for extra_opt in config.cmd_opts.x:  # type: ignore
            if extra_opt == flag:
                return true
    return false


def read_extra_opts(opt: str):
    if config.cmd_opts.x is not None:  # type: ignore
        for extra_opt in config.cmd_opts.x:  # type: ignore
            if extra_opt.startswith(opt):
                attr = extra_opt.split("=")
                if len(attr) == 1:
                    return True
                if len(attr) == 2:
                    return attr[1]
    return None


def load_from_env():
    return has_extra_flag("load_from_env")


def pg_schema():
    return read_extra_opts("pg_schema")


if load_from_env():
    database_config = DatabaseConfig.from_env()
    config.set_main_option("sqlalchemy.url", database_config.url)  # type: ignore


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from llmops_api.base.db.model import Base, CasbinRule, User  # noqa: E402, F401
from llmops_api.model.knowledge import (  # noqa: E402, F401
    Knowledge,
    KnowledgeDocument,
    RetrievalRecord,
    RetrievalRecordChunks,
)
from llmops_api.model.menu import Action, Menu  # noqa: E402, F401
from llmops_api.model.plugins import (  # noqa: E402, F401
    CustomPluginConfig,
    Plugin,
    PluginArgs,
    PluginProvider,
    PluginTagAssociation,
    PluginTags,
)
from llmops_api.model.role import Role  # noqa: E402, F401

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        schema = pg_schema()
        if isinstance(schema, str):
            context.execute(text(f"set search_path to {schema}"))
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
