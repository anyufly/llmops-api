from contextlib import AbstractAsyncContextManager
from typing import Annotated, Callable, List

from casbin import persist
from casbin.model import Model
from casbin.persist.adapters.asyncio import AsyncAdapter
from pydantic import BaseModel, Field
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from llmops_api.base.db.model import CasbinRule


class Filter(BaseModel):
    ptype: Annotated[List[str], Field(default_factory=list)]
    v0: Annotated[List[str], Field(default_factory=list)]
    v1: Annotated[List[str], Field(default_factory=list)]
    v2: Annotated[List[str], Field(default_factory=list)]
    v3: Annotated[List[str], Field(default_factory=list)]
    v4: Annotated[List[str], Field(default_factory=list)]
    v5: Annotated[List[str], Field(default_factory=list)]


class CasbinAdapter(AsyncAdapter):
    def __init__(
        self,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self.transaction_factory = transaction_factory

    def is_filtered(self):
        return True

    async def load_policy(self, model: Model):
        """loads all policy rules from the storage."""
        async with self.transaction_factory() as session:
            lines = await session.scalars(select(CasbinRule))
            for line in lines:
                persist.load_policy_line(str(line), model)

    async def load_filtered_policy(self, model: Model, filter) -> None:
        """loads all policy rules from the storage."""
        async with self.transaction_factory() as session:
            stmt = select(CasbinRule)
            stmt = self.filter_query(stmt, filter)
            result = await session.scalars(stmt)
            for line in result:
                persist.load_policy_line(str(line), model)

    def filter_query(self, stmt, filter):
        for attr in ("ptype", "v0", "v1", "v2", "v3", "v4", "v5"):
            if len(getattr(filter, attr)) > 0:
                stmt = stmt.where(getattr(CasbinRule, attr).in_(getattr(filter, attr)))
        return stmt.order_by(CasbinRule.id)

    async def _save_policy_line(self, ptype, rule):
        # Use session scope (for backward compatibility)
        async with self.transaction_factory() as session:
            line = CasbinRule(ptype=ptype)
            for i, v in enumerate(rule):
                setattr(line, "v{}".format(i), v)
            session.add(line)

    async def save_policy(self, model: Model):
        """saves all policy rules to the storage."""
        async with self.transaction_factory() as session:
            stmt = delete(CasbinRule)
            await session.execute(stmt)
            for sec in ["p", "g"]:
                if sec not in model.model.keys():
                    continue
                for ptype, ast in model.model[sec].items():
                    for rule in ast.policy:
                        await self._save_policy_line(ptype, rule)
        return True

    async def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        await self._save_policy_line(ptype, rule)

    async def add_policies(self, sec, ptype, rules):
        """adds a policy rules to the storage."""

        # Use individual sessions for each rule (original behavior)
        for rule in rules:
            await self._save_policy_line(ptype, rule)

    async def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        async with self.transaction_factory() as session:
            stmt = delete(CasbinRule).where(CasbinRule.ptype == ptype)
            for i, v in enumerate(rule):
                stmt = stmt.where(getattr(CasbinRule, "v{}".format(i)) == v)
            r = await session.execute(stmt)

        return True if r.rowcount > 0 else False

    async def remove_policies(self, sec, ptype, rules):
        """remove policy rules from the storage."""
        if not rules:
            return
        async with self.transaction_factory as session:
            stmt = delete(CasbinRule).where(CasbinRule.ptype == ptype)
            rules = zip(*rules)
            for i, rule in enumerate(rules):
                stmt = stmt.where(or_(getattr(CasbinRule, "v{}".format(i)) == v for v in rule))
            await session.execute(stmt)

    async def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage.
        This is part of the Auto-Save feature.
        """
        async with self.transaction_factory() as session:
            stmt = delete(CasbinRule).where(CasbinRule.ptype == ptype)

            if not (0 <= field_index <= 5):
                return False
            if not (1 <= field_index + len(field_values) <= 6):
                return False
            for i, v in enumerate(field_values):
                if v != "":
                    v_value = getattr(CasbinRule, "v{}".format(field_index + i))
                    stmt = stmt.where(v_value == v)
            r = await session.execute(stmt)

        return True if r.rowcount > 0 else False

    async def update_policy(
        self, sec: str, ptype: str, old_rule: List[str], new_rule: List[str]
    ) -> None:
        async with self.transaction_factory() as session:
            stmt = select(CasbinRule).where(CasbinRule.ptype == ptype)

            # locate the old rule
            for index, value in enumerate(old_rule):
                v_value = getattr(CasbinRule, "v{}".format(index))
                stmt = stmt.where(v_value == value)

            # need the length of the longest_rule to perform overwrite
            longest_rule = old_rule if len(old_rule) > len(new_rule) else new_rule
            result = await session.execute(stmt)
            old_rule_line = result.scalar_one()

            # overwrite the old rule with the new rule
            for index in range(len(longest_rule)):
                if index < len(new_rule):
                    setattr(old_rule_line, "v{}".format(index), new_rule[index])
                else:
                    setattr(old_rule_line, "v{}".format(index), None)

    async def update_policies(
        self,
        sec: str,
        ptype: str,
        old_rules: List[List[str]],
        new_rules: List[List[str]],
    ) -> None:
        for i in range(len(old_rules)):
            await self.update_policy(sec, ptype, old_rules[i], new_rules[i])

    async def update_filtered_policies(
        self, sec, ptype, new_rules: List[List[str]], field_index, *field_values
    ) -> List[List[str]]:
        """update_filtered_policies updates all the policies on the basis of the filter."""

        filter = Filter()
        filter.ptype = ptype

        # Creating Filter from the field_index & field_values provided
        for i in range(len(field_values)):
            if field_index <= i and i < field_index + len(field_values):
                setattr(filter, f"v{i}", field_values[i - field_index])
            else:
                break

        return await self._update_filtered_policies(new_rules, filter)

    async def _update_filtered_policies(self, new_rules, filter) -> List[List[str]]:
        """_update_filtered_policies updates all the policies on the basis of the filter."""

        async with self.transaction_factory() as session:
            # Load old policies

            stmt = select(CasbinRule).where(CasbinRule.ptype == filter.ptype)
            filtered_stmt = self.filter_query(stmt, filter)
            old_rules = await session.scalars(filtered_stmt)

            # Delete old policies

            await self.remove_policies("p", filter.ptype, old_rules)

            # Insert new policies

            await self.add_policies("p", filter.ptype, new_rules)

            # return deleted rules

            return old_rules
