from contextlib import asynccontextmanager

import redis.asyncio as redis

from llmops_api.base.config.config import RedisConfig


class Redis:
    def __init__(self, config: RedisConfig):
        self._pool = redis.ConnectionPool.from_url(config.url)

    async def close(self):
        await self._pool.aclose()

    @asynccontextmanager
    async def client(self):
        client = redis.Redis(connection_pool=self._pool)
        yield client
        await client.aclose()
