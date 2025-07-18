from contextlib import asynccontextmanager, contextmanager

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from llmops_api.base.config import DatabaseConfig


class SyncDatabase:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._engine = create_engine(
            self._config.sync_url,
            connect_args={"server_settings": {"search_path": self._config.db_schema}},
            isolation_level="REPEATABLE READ",
            pool_reset_on_return=None,
            pool_size=self._config.pool.pool_size,
            max_overflow=self._config.pool.max_overflow,
            pool_recycle=self._config.pool.pool_recyle,
            pool_timeout=self._config.pool.pool_timeout,
            echo=self._config.echo,
        )

        self._session_factory = sessionmaker(bind=self._engine, class_=Session)

    @contextmanager
    def session(self):
        with self._session_factory() as session:
            yield session

    @contextmanager
    def transaction_session(self):
        with self._session_factory() as session:
            with session.begin():
                yield session

    def close(self):
        self._engine.dispose()


class Database:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._engine = create_async_engine(
            self._config.url,
            connect_args={"server_settings": {"search_path": self._config.db_schema}},
            isolation_level="REPEATABLE READ",
            pool_reset_on_return=None,
            pool_size=self._config.pool.pool_size,
            max_overflow=self._config.pool.max_overflow,
            pool_recycle=self._config.pool.pool_recyle,
            pool_timeout=self._config.pool.pool_timeout,
            echo=self._config.echo,
        )
        self._session_factory = async_sessionmaker(bind=self._engine, class_=AsyncSession)

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def transaction_session(self):
        async with self._session_factory() as session:
            async with session.begin():
                yield session

    async def close(self):
        await self._engine.dispose()
