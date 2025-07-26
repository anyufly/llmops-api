import asyncio
from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, List, Optional, cast
from uuid import uuid4

from casbin import Model
from loguru._logger import Logger
from pydantic import BaseModel, Field
from redis.asyncio import Redis


class Message(BaseModel):
    method: str = Field(default="")
    local_id: str = Field(default="")
    sec: str = Field(default="")
    ptype: str = Field(default="")
    field_index: int = Field(default=-1)
    rules: List[str | List[str]] = Field(default_factory=list)
    model: str = Field(default="")


class RedisCasbinWatcher:
    def __init__(
        self,
        publish_client_factory: Callable[..., AbstractAsyncContextManager[Redis]],
        logger: Logger,
        channel: str = "casbin",
        subscribe_timeout: int = 2,
        callback: Optional[Callable[[str], Any]] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.local_id = str(uuid4())
        self.publish_client_factory = publish_client_factory
        self.channel = channel
        self.stop_subscribe = False
        self.subscribe_timeout = subscribe_timeout
        self.mutex = asyncio.Lock()
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.callback = callback
        self.logger = logger

    @staticmethod
    def default_callback(msg: str):
        print(f"callback: {msg}")

    async def init_subscribe_client(self):
        async with self.publish_client_factory() as client:
            self.subscribe_client = client.pubsub()

    async def subscribe(self):
        await self.subscribe_client.subscribe(f"channel:{self.channel}")

        while not self.stop_subscribe:
            try:
                message = await self.subscribe_client.get_message(
                    ignore_subscribe_messages=True, timeout=self.subscribe_timeout
                )
                if message is not None:
                    async with self.mutex:
                        callback = self.get_callback()
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message["data"].decode("utf-8"))
                        else:
                            callback(message["data"].decode("utf-8"))
            except Exception as e:
                self.logger.opt(exception=e).error("occured an error when watch casbin")
                continue
        await self.subscribe_client.aclose()

    def stop_subscribe_msg(self):
        self.stop_subscribe = True

    async def set_update_callback(self, callback: Callable[[str], Any]):
        async with self.mutex:
            self.callback = callback

    def get_callback(self) -> Callable[[str], Any]:
        return self.callback if self.callback is not None else self.default_callback

    async def close(self):
        self.stop_subscribe_msg()
        await self.subscribe_client.aclose()

    async def update(self):
        async with self.mutex:
            msg = Message(method="Update", local_id=self.local_id)
            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())

    async def update_for_add_policy(self, sec: str, ptype: str, rule: List[str]):
        async with self.mutex:
            msg = Message(
                method="UpdateForAddPolicy",
                local_id=self.local_id,
                sec=sec,
                ptype=ptype,
                rules=cast(List[str | List[str]], rule),
            )
            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())

    async def update_for_remove_policy(self, sec: str, ptype: str, rule: List[str]):
        async with self.mutex:
            msg = Message(
                method="UpdateForRemovePolicy",
                local_id=self.local_id,
                sec=sec,
                ptype=ptype,
                rules=cast(List[str | List[str]], rule),
            )
            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())

    async def update_for_remove_filtered_policy(
        self, sec: str, ptype: str, field_index: int, rule: List[str]
    ):
        async with self.mutex:
            msg = Message(
                method="UpdateForRemoveFilteredPolicy",
                local_id=self.local_id,
                sec=sec,
                ptype=ptype,
                field_index=field_index,
                rules=cast(List[str | List[str]], rule),
            )
            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())

    async def update_for_save_policy(self, model: Model):
        async with self.mutex:
            msg = Message(
                method="UpdateForSavePolicy",
                local_id=self.local_id,
                model=model.to_text(),
            )

            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())

    async def update_for_add_policies(self, sec: str, ptype: str, rules: List[List[str]]):
        async with self.mutex:
            msg = Message(
                method="UpdateForAddPolicies",
                local_id=self.local_id,
                sec=sec,
                ptype=ptype,
                rules=cast(List[str | List[str]], rules),
            )
            async with self.publish_client_factory() as client:
                return await client.publish(self.channel, msg.model_dump_json())

    async def update_for_remove_policies(self, sec: str, ptype: str, rules: List[List[str]]):
        async with self.mutex:
            msg = Message(
                method="UpdateForRemovePolicies",
                local_id=self.local_id,
                sec=sec,
                ptype=ptype,
                rules=cast(List[str | List[str]], rules),
            )
            async with self.publish_client_factory() as client:
                return await client.publish(f"channel:{self.channel}", msg.model_dump_json())


async def new_watcher(
    publish_client_factory: Callable[..., AbstractAsyncContextManager[Redis]],
    logger: Logger,
    channel: str = "casbin",
    subscribe_timeout: int = 2,
    callback: Optional[Callable[[str], Any]] = None,
) -> RedisCasbinWatcher:
    watcher = RedisCasbinWatcher(
        publish_client_factory,
        logger,
        channel=channel,
        subscribe_timeout=subscribe_timeout,
        callback=callback,
    )
    await watcher.init_subscribe_client()
    watcher.loop.create_task(watcher.subscribe())
    return watcher
