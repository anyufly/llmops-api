import os

import casbin
from loguru._logger import Logger

from llmops_api.base.casbin.adapter import CasbinAdapter
from llmops_api.base.casbin.watcher import Message, RedisCasbinWatcher


async def new_casbin_enforcer(adapter: CasbinAdapter, watcher: RedisCasbinWatcher, logger: Logger):
    casbin_enforcer = CasbinEnforcer(adapter, watcher, logger)
    await casbin_enforcer.init()
    return casbin_enforcer


class CasbinEnforcer:
    def __init__(self, adapter: CasbinAdapter, watcher: RedisCasbinWatcher, logger: Logger):
        self.enforcer = casbin.AsyncEnforcer(os.path.join(os.getcwd(), "rbac_model.conf"), adapter)
        self.watcher = watcher
        self.logger = logger

    async def init(self):
        self.watcher_id = self.watcher.local_id
        await self.watcher.set_update_callback(self._watcher_callback)
        self.enforcer.set_watcher(self.watcher)
        await self.enforcer.load_policy()

    async def _watcher_callback(self, message: str):
        msg = Message.model_validate_json(message)

        if msg.method == "Update":
            self.logger.info(f"Update callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                await self.enforcer.load_policy()
        elif msg.method == "UpdateForAddPolicy":
            self.logger.info(f"UpdateForAddPolicy callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model.add_policy(msg.sec, msg.ptype, msg.rules)
        elif msg.method == "UpdateForRemovePolicy":
            self.logger.info(f"UpdateForRemovePolicy callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model.remove_policy(msg.sec, msg.ptype, msg.rules)
        elif msg.method == "UpdateForRemoveFilteredPolicy":
            self.logger.info(f"UpdateForRemoveFilteredPolicy callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model.remove_filtered_policy(
                    msg.sec, msg.ptype, msg.field_index, *msg.rules
                )
        elif msg.method == "UpdateForSavePolicy":
            self.logger.info(f"UpdateForSavePolicy callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model = self.enforcer.model.load_model_from_text(msg.model)
        elif msg.method == "UpdateForAddPolicies":
            self.logger.info(f"UpdateForAddPolicies callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model.add_policies(msg.sec, msg.ptype, msg.rules)
        elif msg.method == "UpdateForRemovePolicies":
            self.logger.info(f"UpdateForRemovePolicies callback msg recieved, msg:{message}")
            if msg.local_id != self.watcher_id:
                self.enforcer.model.remove_policies(msg.sec, msg.ptype, msg.rules)
        else:
            self.logger.warning(f"unknown callback msg recieved, msg:{message},skip...")
